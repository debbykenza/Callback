"""Endpoint WebSocket pour l'entretien vocal (V2, Gemini Live).

Le routeur est volontairement mince : toute la logique (relais audio, appel
d'outil, sauvegarde des transcripts) vit dans `app.services.voice_service`.
"""

from fastapi import APIRouter, WebSocket

from app.services.voice_service import VoiceInterviewRelay

router = APIRouter(tags=["voice"])


@router.websocket("/ws/sessions/{session_id}/voice")
async def voice_interview(websocket: WebSocket, session_id: str):
    relay = VoiceInterviewRelay(session_id)
    await relay.run(websocket)
