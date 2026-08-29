# Run Doc — SIF Precursor Intelligence System

## How to Reproduce Uncommitted Artifacts
1. Copy `.env` from main checkout (contains GEMINI_API_KEY)
2. Frontend is already built in `frontend/dist/`
3. Python deps: `pip install -r requirements.txt`
4. spaCy model: `python -m spacy download en_core_web_sm`

## How to Run the Server
1. Start FastAPI backend on port 8000
2. Frontend served from `frontend/dist/` by FastAPI static mount
3. Open http://localhost:5173 for dev server OR http://localhost:8000 for production build
