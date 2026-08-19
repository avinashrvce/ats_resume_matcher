# ResumeMatch

ResumeMatch is a web app that analyzes a resume against a job description and provides:

- ATS compatibility score
- keyword gap analysis
- improvement suggestions
- a tailored resume draft

## Features

- Upload a resume in PDF format
- Paste a job description
- Run analysis through a Python backend
- Use Gemini as the LLM provider
- View ATS score and recommendations in the browser

## Tech Stack

- Python
- Flask
- HTML / JavaScript
- Google Gemini API
- PyPDF

## Project Structure

- `app.py` — Flask backend
- `ats-resume-matcher.html` — frontend UI
- `.env` — local environment variables
- `.env.example` — sample environment file
- `requirements.txt` — Python dependencies

## Architecture

Browser
   ↓
Flask REST API
   ↓
PDF Text Extraction
   ↓
Prompt Construction
   ↓
Gemini LLM
   ↓
Structured JSON
   ↓
ATS Analysis + Tailored Resume

## Security

- API key in environment
- No original resume persistence
- file size validation
- production considerations

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file using the sample:

   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   GEMINI_MODEL=gemini-3.5-flash
   PORT=5000
   ```

4. Run the app:

   ```bash
   python app.py
   ```

5. Open the app in your browser:

   ```text
   http://127.0.0.1:5000
   ```

## Notes

- The app expects a PDF resume and a job description text.
- Keep your API key in a local `.env` file and do not commit it to source control.
- `.env` is already ignored in `.gitignore`.
