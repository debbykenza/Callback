# Callback — coach d'entretien IA

Simulateur d'entretien d'embauche : tu colles une offre, tu donnes ton CV, tu
choisis une persona de recruteur, et l'IA mène un entretien qui s'adapte à tes
réponses (relance si tu restes trop vague, question suivante sinon). À la fin,
tu obtiens une fiche récapitulative (points forts / points à travailler /
notes par critère), et un historique de tous tes entretiens passés.

Deux modes d'entretien sont disponibles : **par écrit** (rien à configurer,
fonctionne tout de suite avec le fournisseur `mock`), et **à l'oral** — un
vrai échange voix-à-voix façon Siri, via l'API gratuite Google Gemini Live
(bouton « 🎙️ Mode vocal » sur l'écran d'entretien). Voir
[Le mode vocal (V2, Gemini Live)](#le-mode-vocal-v2-gemini-live) plus bas
pour la configuration et les limites à connaître.

## Ce qui est déjà là

- **RAG léger** : chaque CV est découpé en fragments (une expérience = un
  fragment), chacun embeddé. Quand l'IA pose une question sur une compétence,
  elle va chercher le fragment de CV le plus pertinent (similarité cosinus)
  et s'appuie dessus pour poser une question ancrée dans du concret plutôt
  que générique.
- **Relances adaptatives** : après chaque réponse à une question de
  compétence, l'IA évalue si c'est assez concret. Si c'est vague, elle relance
  une fois ("donne un exemple précis") avant de passer à la suite.
- **Fiche récapitulative générée** : à la fin, un appel LLM récapitule le
  transcript en points forts / points à travailler / notes par critère
  (clarté technique, structure des réponses, gestion des relances).
- **Historique + retry** : chaque entretien est stocké (CV utilisé, offre,
  persona, transcript, fiche). Depuis l'historique, tu peux retenter un
  entretien avec les mêmes CV/offre/persona.
- **Fournisseur LLM interchangeable** : le code ne dépend d'aucun fournisseur
  en particulier (voir [Fournisseurs LLM](#fournisseurs-llm) plus bas).
- **Mode vocal (Gemini Live)** : bascule à tout moment entre entretien écrit
  et entretien à l'oral (voix-à-voix, function calling en plein milieu de la
  conversation) — voir [Le mode vocal](#le-mode-vocal-v2-gemini-live) plus
  bas.

## Architecture

```
callback-project/
├── backend/            FastAPI + SQLAlchemy + Postgres
│   └── app/
│       ├── models.py        modeles de donnees (CV, offre, session, messages, fiche)
│       ├── llm/              interface LLMProvider + implementations mock/ollama/openai
│       ├── services/         logique metier (parsing CV/offre, entretien adaptatif, fiche)
│       └── routers/          endpoints API
├── frontend/            SvelteKit + Tailwind (4 ecrans : setup, entretien, fiche, historique)
├── sample_data/          un CV et une offre d'exemple pour tester tout de suite
├── e2e/                  test de bout en bout optionnel (Playwright)
└── docker-compose.yml    Postgres pret a l'emploi
```

Le principe : **rien ne dépend d'une clé API pour tourner en local**. Par
défaut, `LLM_PROVIDER=mock` simule des réponses structurellement réalistes
(mêmes heuristiques que le "vrai" flow, sans appeler de modèle) — tu peux donc
lancer tout le projet et le montrer en entretien sans avoir configuré quoi que
ce soit. Dès que tu veux de vraies réponses générées par un modèle, un
changement de variable d'environnement suffit (voir plus bas).

## Lancer le projet

### 1. Base de données

```bash
docker compose up -d
```

Ça lance Postgres sur `localhost:5432` (utilisateur/mot de passe/base :
`callback`). Rien d'autre à configurer.

### 2. Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

L'API est documentée automatiquement sur http://localhost:8000/docs
(Swagger) — pratique pour tester les endpoints sans passer par le frontend.

### 3. Frontend

Dans un autre terminal :

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Ouvre http://localhost:5173 — tu peux utiliser `sample_data/cv_exemple.pdf`
et `sample_data/offre_exemple.txt` pour tester immédiatement sans avoir ton
propre CV sous la main.

## Fournisseurs LLM

Le code ne connaît jamais le fournisseur concret : toute la logique métier
(`app/services/`) parle à l'interface `LLMProvider` / `EmbeddingProvider`
(`app/llm/base.py`). Trois implémentations existent déjà, sélectionnées par
`LLM_PROVIDER` dans `backend/.env` :

| Valeur | Ce que ça donne | Prérequis |
|---|---|---|
| `mock` (défaut) | Réponses simulées par heuristiques, aucune vraie intelligence, mais 100% gratuit et hors-ligne | rien |
| `gemini` | Vrai modèle via l'API Gemini (gratuite) | `GEMINI_API_KEY` dans `.env` (même clé que le mode vocal) |
| `ollama` | Vrai modèle en local (ex. Llama 3.1) | [Ollama](https://ollama.com) installé, `ollama pull llama3.1` + `ollama pull nomic-embed-text` |
| `openai` | Vrai modèle via l'API OpenAI | `OPENAI_API_KEY` dans `.env`, facturé à l'usage |

**Attention** si tu changes de fournisseur après avoir déjà uploadé des CV :
les embeddings stockés ne sont pas comparables d'un fournisseur à l'autre
(dimensions différentes). Ré-uploade le CV après un changement de
`LLM_PROVIDER`.

### Pourquoi les questions du mode `mock` semblent génériques

Le fournisseur `mock` (celui utilisé par défaut) ne comprend rien : il repère
des compétences en cherchant des mots dans une liste fixe d'une quarantaine de
termes (`app/llm/mock_provider.py`, `KNOWN_SKILLS`), et cette liste est
biaisée vers le développement web/fullstack (React, FastAPI, PostgreSQL,
PHP...) parce que c'est le profil utilisé pour la construire. Résultat : pour
un CV ou une offre dans un autre domaine (data, mécanique, marketing...), très
peu de mots correspondent, et le peu qui reste (`SQL`, `REST`...) revient tout
le temps — d'où des questions qui semblent identiques d'un profil à l'autre.
Ce n'est pas un bug d'affichage, c'est la limite assumée du fournisseur
gratuit hors-ligne.

**La solution : passe sur `LLM_PROVIDER=gemini`** (`backend/app/llm/gemini_provider.py`).
Il utilise un vrai modèle de langage (même clé Gemini gratuite que le mode
vocal, pas besoin d'en créer une autre) pour lire le CV et l'offre et en
extraire les compétences réellement mentionnées, quel que soit le domaine —
plus de liste figée, donc plus de biais web/fullstack. Il suffit de mettre
`LLM_PROVIDER=gemini` et `GEMINI_API_KEY=...` dans `backend/.env`, puis de
relancer le backend et de ré-uploader le CV et l'offre (les embeddings
changent de fournisseur, voir l'avertissement ci-dessus).

*Honnêtement* : comme pour le mode vocal, ce fournisseur a été écrit et
vérifié contre le SDK `google-genai` installé (signatures exactes des
méthodes `generate_content`/`embed_content`, testées avec des réponses
simulées), mais pas appelé en vrai contre l'API Gemini — l'environnement de
construction du projet n'a pas accès réseau à Google. Teste-le sur un cas
simple avant de t'y fier.

## Tests

- `backend/smoke_test.py` : test de bout en bout du backend seul (CV → offre
  → entretien → relance → fin → fiche → historique → retry), avec SQLite et
  le fournisseur mock. `cd backend && source .venv/bin/activate && python
  smoke_test.py`.
- `e2e/test_flow.mjs` : le même parcours mais dans un vrai navigateur
  (Playwright), backend + frontend lancés en même temps. Optionnel — voir les
  instructions en haut du fichier.

Les deux ont été exécutés pendant la construction de ce projet, avec succès.

## Authentification

Inscription / connexion par email + mot de passe (hashé avec bcrypt), token
JWT stocké côté frontend et envoyé dans le header `Authorization: Bearer
<token>`. CV, offres, entretiens et historique sont rattachés à l'utilisateur
connecté (`user_id`) — un compte ne voit jamais les données d'un autre.

- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`.
- Configuration : `JWT_SECRET_KEY` / `JWT_ALGORITHM` / `JWT_EXPIRE_MINUTES`
  dans `.env` (voir `.env.example`) — **change `JWT_SECRET_KEY` avant tout
  déploiement**, la valeur par défaut n'est que pour le dev local.
- Frontend : `src/lib/auth.js` (store + localStorage) et `src/lib/api.js`
  (ajout automatique du header sur les appels protégés), pages
  `/login` et `/signup`, garde de route dans `+layout.svelte`.

## Limites connues (honnêtement)

- Pas de vérification d'email ni de réinitialisation de mot de passe pour
  l'instant — inscription/connexion/déconnexion basiques seulement.
- Le canal vocal (WebSocket `/ws/sessions/{id}/voice`) n'est pas encore
  protégé par ce système d'auth : un WebSocket natif ne peut pas envoyer de
  header `Authorization`, il faudrait lui passer le token en paramètre de
  requête et le vérifier côté backend. À faire si tu pousses ce projet plus
  loin.
- Pas de migrations Alembic pour les nouvelles colonnes (`user_id`, table
  `users`) : comme le reste du schéma, tout est recréé par
  `Base.metadata.create_all` — si tu as déjà une base locale avec des données
  de test, le plus simple est de la supprimer et de la relancer.
- Pas de migrations Alembic : les tables sont créées automatiquement au
  démarrage (`Base.metadata.create_all`). Suffisant ici, mais dans un vrai
  projet en production tu voudrais des migrations versionnées.
- La recherche RAG compare les embeddings en Python (cosinus), pas via
  `pgvector` : très bien pour un CV (quelques dizaines de fragments max), mais
  ne passerait pas à l'échelle sur un vrai corpus. Le prochain pas naturel
  serait d'ajouter l'extension `pgvector` à Postgres.
- L'évaluation "réponse vague ou pas" (fournisseur mock) est une heuristique
  simple (longueur + quelques marqueurs) — avec Ollama/OpenAI, c'est un vrai
  appel LLM qui juge, donc plus fin.

## Le mode vocal (V2, Gemini Live)

L'entretien 100% vocal (façon Siri) fonctionne via l'API **Gemini Live** de
Google (voix-à-voix, gratuite avec une clé perso). Architecture : le
navigateur envoie l'audio du micro au **backend** par WebSocket, le backend
relaie vers Gemini Live (et inversement pour l'audio de réponse) — la clé API
Gemini ne quitte jamais le serveur.

```
navigateur (micro/haut-parleur)
   │  WebSocket /ws/sessions/{id}/voice  (audio brut PCM16 + JSON transcript/status)
   ▼
backend FastAPI (app/services/voice_service.py)
   │  API Gemini Live (voix-à-voix + function calling)
   ▼
Gemini Live
```

### L'effet visio (caméra + visage animé)

Le mode vocal se présente comme un vrai appel vidéo, avec deux tuiles côte à
côte : la persona et toi (ta propre caméra, en miroir, comme un retour vidéo
classique). Important : **ta caméra ne sert qu'à cet affichage local** —
l'image n'est jamais envoyée au backend ni à Gemini, seul l'audio l'est. Si
la caméra est refusée ou absente, l'entretien continue normalement en audio
seul (la tuile affiche juste un message à la place du flux vidéo).

La tuile de la persona affiche un **visage illustré animé**
(`frontend/src/lib/components/PersonaFace.svelte`, dessiné en SVG, aucune
image ni service externe) qui réagit en temps réel : la bouche s'ouvre et se
ferme au rythme du volume de la voix de réponse (analysée côté navigateur
via un `AnalyserNode` sur l'audio de sortie), les yeux clignent
périodiquement, et le visage s'incline légèrement quand c'est toi qui parles
(même principe, sur le volume du micro). Chaque persona a une silhouette de
cheveux différente (`personaHairStyle()` dans `frontend/src/lib/personas.js`)
pour rester reconnaissable d'un coup d'œil. C'est un rendu illustré/stylisé,
pas une vidéo photoréaliste avec lip-sync — un avatar vidéo de ce niveau
demande un service payant facturé à la minute (D-ID, HeyGen...), hors de
portée d'un projet gratuit comme celui-ci.

### Configuration

1. Récupère une clé gratuite sur [aistudio.google.com](https://aistudio.google.com)
   (bouton « Get API key » dans le menu de gauche → « Create API key »).
2. Dans `backend/.env`, renseigne `GEMINI_API_KEY=ta-cle`.
3. Relance le backend (`uvicorn app.main:app --reload --port 8000`) — rien
   d'autre à configurer, `google-genai` est déjà dans `requirements.txt`.
4. Sur l'écran d'entretien, clique sur « 🎙️ Mode vocal », autorise l'accès au
   micro dans ton navigateur, et parle normalement.

### Ce que ça fait

- Le même déroulé qu'à l'écrit (présentation, une question par compétence
  requise, une relance si la réponse reste vague, question de clôture) est
  passé en consigne système à Gemini Live — c'est le prompt qui pilote la
  conversation, puisque l'API vocale ne connaît pas la machine à états du
  mode texte.
- Gemini peut appeler un outil `lookup_cv` (function calling en plein milieu
  de la conversation) pour retrouver un extrait pertinent du CV avant de
  poser une question — même recherche RAG que le mode texte.
- Chaque tour de parole (transcription input/output fournie par Gemini) est
  sauvegardé comme message en base, exactement comme à l'écrit : la fiche
  récapitulative et l'historique fonctionnent donc à l'identique, que
  l'entretien se soit fait à l'oral ou à l'écrit (voire un mélange des deux
  en passant de l'un à l'autre).
- Voix disponibles côté Gemini : `Puck`, `Charon`, `Kore`, `Fenrir`, `Aoede`
  — une voix par persona, réglable via `GEMINI_VOICE_MAP_*` dans `.env`.

### Limites connues (honnêtement)

- **Non testé en conditions réelles** : ce module a été écrit et vérifié
  contre le SDK `google-genai` installé (noms de champs, signatures exactes),
  mais l'environnement où ce projet a été construit n'a ni clé API Gemini, ni
  micro/navigateur réel, et son accès réseau sortant bloque l'endpoint de
  Gemini Live — impossible d'y faire un vrai aller-retour audio avant de te
  livrer le projet. Teste-le en premier avec un cas simple avant de t'y fier
  pour une démo ; si le comportement observé ne correspond pas à ce qui est
  décrit ici, active les `print()` déjà en place dans
  `_forward_gemini_to_browser` (`backend/app/services/voice_service.py`) pour
  voir la forme exacte des messages reçus de Gemini.
- Utilise `ScriptProcessorNode` côté navigateur (API dépréciée mais simple et
  largement supportée) plutôt qu'un `AudioWorklet` séparé — largement
  suffisant pour un usage portfolio.
- Limites côté Gemini Live (gratuit) : session vocale d'environ 15 minutes de
  contexte audio, connexion WebSocket sous-jacente à reprendre au-delà
  d'environ 10 minutes (non géré ici — pour un entretien de quelques minutes
  ça ne se pose pas).
#   C a l l b a c k  
 