# ResumeMatch

ResumeMatch is a web app that analyzes a resume against a job description and provides:

- ATS compatibility score
- keyword gap analysis
- improvement suggestions
- an optional tailored resume draft generated after confirmation

## Features

- Upload a resume in PDF format
- Paste a job description
- Run analysis through a Python backend
- Use Gemini as the LLM provider
- View ATS score and recommendations in the browser
- Choose whether to generate a tailored resume after reviewing the score

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

## Run with Docker

1. Install and start [Docker Desktop](https://www.docker.com/products/docker-desktop/).

2. In the project folder, create `.env` from the example if it does not already
   exist, then add a valid Gemini API key:

   ```powershell
   Copy-Item .env.example .env
   ```

   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   GEMINI_MODEL=gemini-3.5-flash
   PORT=5000
   ```

3. Build and start the container:

   ```powershell
   docker compose up --build -d
   ```

4. Open http://localhost:5000.

Useful commands:

```powershell
# Follow application logs
docker compose logs -f

# Stop and remove the container
docker compose down

# Rebuild after changing application code or dependencies
docker compose up --build -d
```

The `.env` file is passed to the container at runtime and excluded from the
image build context, so do not commit it to Git.

## Notes

- The app expects a PDF resume and a job description text.
- Keep your API key in a local `.env` file and do not commit it to source control.
- `.env` is already ignored in `.gitignore`.
