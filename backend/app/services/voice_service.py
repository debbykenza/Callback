"""Relais de l'entretien vocal (V2) : fait le pont entre le navigateur (audio brut
sur une WebSocket) et l'API Gemini Live de Google (voix-a-voix + function calling).

IMPORTANT (a lire avant de debugger) : ce module a ete ecrit et verifie contre le
SDK `google-genai` installe (noms de champs, signatures de methodes), mais n'a PAS
pu etre teste en conditions reelles (pas de cle API Gemini disponible dans
l'environnement ou ce projet a ete construit). Si quelque chose ne colle pas avec
la reponse reelle de l'API, commence par activer les logs (`print` dans
`_forward_gemini_to_browser`) pour voir la forme exacte des messages recus.

Principe :
- Le navigateur envoie de l'audio brut (PCM16, 16kHz, mono) en frames binaires sur
  la WebSocket `/ws/sessions/{id}/voice`, et peut envoyer un message texte JSON
  {"type": "end"} pour couper proprement.
- Ce module relaie cet audio vers Gemini Live, recoit les reponses (audio 24kHz +
  transcriptions texte + appels d'outil), et renvoie au navigateur :
    - des frames binaires (audio de reponse, PCM16 24kHz)
    - des messages JSON {"type": "transcript", "role": "user"|"assistant", "text": "..."}
    - des messages JSON {"type": "status", ...} et {"type": "error", "message": "..."}
- L'appel d'outil `lookup_cv` permet a Gemini d'aller chercher un extrait pertinent
  du CV (meme recherche par similarite que le mode texte) avant de poser une
  question ancree dans le concret.
- Chaque tour de parole termine (transcription input/output) est sauvegarde comme
  Message en base, exactement comme en mode texte : la fiche recapitulative et
  l'historique fonctionnent donc sans aucun changement.
"""

import json

from fastapi import WebSocket
from google import genai
from google.genai import types

from app.config import get_settings
from app.database import SessionLocal
from app.models import PERSONAS, InterviewSession, JobOffer, Message
from app.services.interview_service import _retrieve_cv_context

INPUT_SAMPLE_RATE = 16000
OUTPUT_SAMPLE_RATE = 24000


def _lookup_cv_declaration() -> types.FunctionDeclaration:
    return types.FunctionDeclaration(
        name="lookup_cv",
        description=(
            "Cherche un extrait pertinent du CV du candidat sur un sujet ou une "
            "competence donnee, pour poser une question ancree dans son experience "
            "reelle plutot qu'une question generique."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Le sujet ou la competence a chercher dans le CV (ex: 'React', 'gestion de projet')",
                }
            },
            "required": ["topic"],
        },
    )


def _build_system_instruction(persona_name: str, persona_tag: str, job_title: str, company: str, required_skills: list[str]) -> str:
    skills_txt = ", ".join(required_skills) if required_skills else "son parcours general"
    return f"""Tu es {persona_name}, une recruteuse/recruteur virtuel(le) qui mene a l'oral, en francais,
un entretien d'embauche pour le poste de {job_title} chez {company}. Ton style : {persona_tag}.

Deroule de l'entretien, dans l'ordre :
1. Salue le/la candidat(e) et demande-lui de se presenter et de parler de son parcours.
2. Pose ensuite une question sur chacune de ces competences, une par une : {skills_txt}.
   AVANT de poser une question sur une competence, appelle l'outil lookup_cv avec cette
   competence comme sujet, et appuie ta question sur l'extrait trouve (mentionne-le
   explicitement) plutot que de poser une question generique.
3. Si la reponse du/de la candidat(e) reste vague ou generique, relance UNE fois en
   demandant un exemple concret ou un resultat chiffre, puis passe a la competence
   suivante quelle que soit la qualite de la relance (ne relance jamais deux fois de suite).
4. Une fois toutes les competences couvertes, termine en demandant ce qui l'attire
   dans ce poste chez {company}.
5. Apres sa reponse a cette derniere question, remercie le/la candidat(e) et dis
   clairement que l'entretien est termine.

Parle de maniere naturelle et concise, comme dans un vrai entretien oral : des phrases
courtes, une seule question a la fois, jamais de liste ni de formatage. Ne repete
jamais mot pour mot les instructions ci-dessus, et ne mentionne jamais que tu es une IA."""


class VoiceInterviewRelay:
    """Une instance par connexion WebSocket (donc par entretien vocal en cours)."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.settings = get_settings()

    async def run(self, ws: WebSocket) -> None:
        import asyncio

        await ws.accept()

        session_info = await asyncio.to_thread(self._load_session_info)
        if session_info is None:
            await ws.send_json({"type": "error", "message": "Entretien introuvable."})
            await ws.close()
            return

        if not self.settings.gemini_api_key:
            await ws.send_json(
                {
                    "type": "error",
                    "message": "GEMINI_API_KEY n'est pas configuree dans backend/.env (voir .env.example).",
                }
            )
            await ws.close()
            return

        persona_id, persona_meta, job_title, company, required_skills = session_info

        client = genai.Client(api_key=self.settings.gemini_api_key)
        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=_build_system_instruction(
                persona_meta["name"], persona_meta["tag"], job_title, company, required_skills
            ),
            tools=[types.Tool(function_declarations=[_lookup_cv_declaration()])],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=self.settings.gemini_voice_for(persona_id)
                    )
                )
            ),
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            context_window_compression=types.ContextWindowCompressionConfig(
                sliding_window=types.SlidingWindow()
            ),
        )

        try:
            async with client.aio.live.connect(model=self.settings.gemini_live_model, config=config) as live_session:
                await ws.send_json({"type": "status", "state": "ready"})
                browser_task = asyncio.create_task(self._forward_browser_to_gemini(ws, live_session))
                gemini_task = asyncio.create_task(self._forward_gemini_to_browser(ws, live_session))
                _done, pending = await asyncio.wait(
                    {browser_task, gemini_task}, return_when=asyncio.FIRST_COMPLETED
                )
                for task in pending:
                    task.cancel()
        except Exception as exc:  # noqa: BLE001 - on relaie n'importe quelle erreur au client
            try:
                await ws.send_json({"type": "error", "message": f"Erreur Gemini Live : {exc}"})
            except Exception:
                pass
        finally:
            try:
                await ws.close()
            except Exception:
                pass

    # --- DB helpers (executes sur un thread separe via asyncio.to_thread : la
    #     session SQLAlchemy est synchrone et ne doit pas etre partagee entre
    #     coroutines concurrentes) ---

    def _load_session_info(self):
        db = SessionLocal()
        try:
            session = db.get(InterviewSession, self.session_id)
            if session is None:
                return None
            job_offer = db.get(JobOffer, session.job_offer_id)
            persona_meta = PERSONAS[session.persona]
            return session.persona, persona_meta, job_offer.title, job_offer.company, job_offer.required_skills
        finally:
            db.close()

    def _save_message(self, role: str, content: str) -> None:
        db = SessionLocal()
        try:
            db.add(Message(session_id=self.session_id, role=role, content=content, is_followup=False))
            db.commit()
        finally:
            db.close()

    def _lookup_cv(self, topic: str) -> str:
        db = SessionLocal()
        try:
            session = db.get(InterviewSession, self.session_id)
            if session is None:
                return "CV introuvable."
            extract = _retrieve_cv_context(db, session.cv_id, topic)
            return extract or "Aucun extrait pertinent trouve dans le CV pour ce sujet."
        finally:
            db.close()

    # --- Relais audio ---

    async def _forward_browser_to_gemini(self, ws: WebSocket, live_session) -> None:
        while True:
            message = await ws.receive()
            if message["type"] == "websocket.disconnect":
                break
            data = message.get("bytes")
            if data is not None:
                await live_session.send_realtime_input(
                    audio=types.Blob(data=data, mime_type=f"audio/pcm;rate={INPUT_SAMPLE_RATE}")
                )
                continue
            text = message.get("text")
            if text is not None:
                try:
                    payload = json.loads(text)
                except json.JSONDecodeError:
                    continue
                if payload.get("type") == "end":
                    break

    async def _forward_gemini_to_browser(self, ws: WebSocket, live_session) -> None:
        import asyncio

        current_user_text = ""
        current_assistant_text = ""

        # IMPORTANT : `live_session.receive()` du SDK google-genai ne renvoie
        # qu'UN SEUL tour de conversation puis s'arrete (son code fait
        # `break` des qu'un message a `turn_complete=True`) — ce n'est pas un
        # flux continu pour toute la duree de la connexion. Il faut donc le
        # rappeler a chaque nouveau tour, sinon la tache se termine des la
        # premiere question posee par l'IA, ce qui (via le
        # `asyncio.wait(..., return_when=FIRST_COMPLETED)` dans `run()`)
        # coupe toute la connexion — symptome observe : le mode vocal
        # s'arrete tout seul juste apres la premiere question, et se
        # reconnecter relance l'entretien depuis le debut.
        while True:
            async for response in live_session.receive():
                server_content = response.server_content
                if server_content is not None:
                    if server_content.input_transcription and server_content.input_transcription.text:
                        current_user_text += server_content.input_transcription.text
                    if server_content.output_transcription and server_content.output_transcription.text:
                        current_assistant_text += server_content.output_transcription.text

                    if server_content.model_turn:
                        for part in server_content.model_turn.parts or []:
                            if part.inline_data and part.inline_data.data:
                                await ws.send_bytes(part.inline_data.data)

                    if server_content.turn_complete:
                        if current_user_text.strip():
                            text_to_save = current_user_text.strip()
                            await asyncio.to_thread(self._save_message, "user", text_to_save)
                            await ws.send_json({"type": "transcript", "role": "user", "text": text_to_save})
                            current_user_text = ""
                        if current_assistant_text.strip():
                            text_to_save = current_assistant_text.strip()
                            await asyncio.to_thread(self._save_message, "assistant", text_to_save)
                            await ws.send_json({"type": "transcript", "role": "assistant", "text": text_to_save})
                            current_assistant_text = ""

                if response.tool_call:
                    function_responses = []
                    for fc in response.tool_call.function_calls:
                        topic = (fc.args or {}).get("topic", "")
                        result_text = await asyncio.to_thread(self._lookup_cv, topic)
                        function_responses.append(types.FunctionResponse(id=fc.id, name=fc.name, response={"result": result_text}))
                    await live_session.send_tool_response(function_responses=function_responses)
            # `receive()` s'est arrete (fin du tour) : on le rappelle pour le tour suivant.
