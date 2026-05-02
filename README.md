# EcoTour AI Pakistan

EcoTour AI is a full-stack travel assistant for Pakistan with:

- AI-style trip planning with budget slider support
- Distance and dynamic cost estimation (example: Islamabad -> Skardu)
- English/Urdu chatbot flow
- Crisis helper tab inspired by Rahat AI use case
- Emergency quick-call buttons for mobile users
- Voice transcription endpoint using Whisper (optional install)
- SQLite storage now, Supabase-ready upgrade path

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Whisper Voice Integration

Install Whisper when you are ready:

```bash
pip install openai-whisper
```

Then upload audio from the UI in the chatbot section.

## Supabase Integration (Next Step)

1. Create a Supabase project and get:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
2. Create tables equivalent to:
   - `trip_requests`
   - `chat_messages`
3. Replace `sqlite` calls in `app/main.py` with Supabase SDK calls or keep FastAPI + Postgres via SQLAlchemy.
4. Move emergency, trip and chat persistence to Supabase for cloud sync.

If you want, I can do this integration in the next pass as soon as you share your Supabase keys and preferred backend approach.

## Project Structure

```text
app/
  main.py
  database.py
  models.py
  schemas.py
  data/knowledge.py
  services/
    planner.py
    chat.py
    crisis.py
  templates/index.html
  static/styles.css
  static/app.js
```
