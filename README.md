# Kabaybay AI
Read. Reflect. Find comfort through Scripture.

## Run locally
    pip install -r requirements.txt
    streamlit run streamlit_app.py

## Bible data
Add a verified KJV or WEB file at `data/bible_verses.csv` with columns
`book,testament,chapter,verse,reference,text` (optional: `translation`).
Until it is present and usable, the app shows a warning and displays no Scripture.

## AI reflection
The optional AI reflection uses Groq without exposing the API key. Set
`GROQ_API_KEY` or the existing `AI_API_KEY`, and optionally `GROQ_MODEL` or
`AI_MODEL`, in environment variables, a local `.env` file, or Streamlit Secrets.
The Vent Your Heart page automatically selects a complete passage from the loaded dataset
after submission. The app sends only the user's emotion, message, and selected
verified passage. Crisis messages are handled locally before any AI call.

## Status
Home, Bible Library, Vent Your Heart, verified passage retrieval, and AI reflection are available.
