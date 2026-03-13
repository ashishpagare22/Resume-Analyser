# AI Resume Analyzer

A lightweight Streamlit app that compares a resume against a job description and produces:

- an overall match score
- matched and missing keywords
- section-level feedback
- concrete improvement suggestions

## Features

- Paste a resume and job description directly into the app
- Get an ATS-style score based on keyword and section coverage
- Surface missing skills and action verbs
- Show concise recommendations to improve the resume

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
streamlit run app.py
```

## Project structure

- `app.py` - Streamlit interface
- `src/analyzer.py` - resume analysis logic

## Notes

- This first version uses deterministic text analysis, so it works without any API keys.
- You can extend the scoring logic later with embeddings or LLM-based feedback if you want.
