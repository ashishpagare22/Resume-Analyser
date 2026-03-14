# AI Resume Analyzer

A lightweight Streamlit app that compares a resume against a job description and produces:

- an overall match score
- matched and missing keywords
- section-level feedback
- concrete improvement suggestions
- practical rewrite ideas and next-step guidance

## Features

- Upload a resume PDF or paste resume text
- Upload a job description PDF or paste job description text
- Get an ATS-style score based on keyword, section, and impact coverage
- Surface missing skills, weak sections, and low-impact bullet patterns
- Show practical recommendations and rewrite examples

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
