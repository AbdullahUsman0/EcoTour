# EcoTour AI Pakistan

EcoTour AI is a full-stack travel assistant for Pakistan with:

- AI-style trip planning with budget slider support
- Distance and dynamic cost estimation (example: Islamabad -> Skardu)
- English/Urdu chatbot flow
- Crisis helper tab inspired by Rahat AI use case
- Emergency quick-call buttons for mobile users
- Voice transcription endpoint using Whisper + speech output using TTS
- Supabase persistence for trips and chat
- Live weather + fare pressure signal integration for dynamic pricing
- LLM itinerary generation for smarter trip plans
- Multi-provider live AI chat (OpenAI, Groq, OpenRouter)
- RAG-grounded answers using in-app travel knowledge base
- AI trip options with do-now and avoid-now guidance
- Floating AI assistant widget on every screen
- Enter-to-send chat and microphone recording for Whisper transcription
- Live route distance via OSRM and hotel suggestions via Overpass

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Environment Setup

Copy `.env.example` to `.env` and set:

- `SUPABASE_URL`
- `SUPABASE_KEY`
- `AI_PROVIDER` (`openai`, `groq`, `openrouter`)
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (optional)
- `GROQ_API_KEY` and `GROQ_MODEL` (optional)
- `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` (optional)

## Supabase Tables

Run this SQL in your Supabase SQL editor:

```sql
create table if not exists trip_requests (
  id bigint generated always as identity primary key,
  origin text not null,
  destination text not null,
  budget double precision not null,
  travelers int not null,
  language text not null,
  estimated_distance_km double precision not null,
  estimated_cost double precision not null,
  weather_note text,
  fare_note text,
  created_at timestamptz default now()
);

create table if not exists chat_messages (
  id bigint generated always as identity primary key,
  user_message text not null,
  assistant_message text not null,
  language text not null,
  created_at timestamptz default now()
);
```

## Voice Integration

Install Whisper + TTS dependencies:

```bash
pip install openai-whisper gTTS
```

Then:
- Upload voice in chatbot section for speech-to-text.
- Click "Speak Last Reply" for text-to-speech audio.

## Project Structure

```text
app/
  main.py
  config.py
  schemas.py
  data/knowledge.py
  services/
    planner.py
    chat.py
    crisis.py
    external_signals.py
    llm.py
    supabase_store.py
  templates/index.html
  static/styles.css
  static/app.js
```
