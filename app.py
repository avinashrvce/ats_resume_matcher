import json
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import google.generativeai as genai
from pypdf import PdfReader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")


def extract_pdf_text(pdf_bytes: bytes) -> str:
    try:
        reader = PdfReader(__import__("io").BytesIO(pdf_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
        return "\n\n".join(pages).strip()
    except Exception:
        return "" 


def build_prompt(job_description: str, resume_text: str) -> str:
    return f"""You are an expert ATS (Applicant Tracking System) analyst and resume coach.
Never invent experience, skills, certifications, achievements, employers, metrics or technologies not present in the source resume.
    
Below is the candidate resume text extracted from the PDF, and the job description to compare against.

RESUME TEXT:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return ONLY a valid JSON object (no markdown, no explanation) with this exact structure:
{{
  "ats_score": <integer 0-100>,
  "grade": "<Excellent|Good|Fair|Poor>",
  "breakdown": [
    {{"label": "Keyword Match", "score": <0-100>}},
    {{"label": "Skills Alignment", "score": <0-100>}},
    {{"label": "Experience Relevance", "score": <0-100>}},
    {{"label": "Education Match", "score": <0-100>}},
    {{"label": "Formatting & Readability", "score": <0-100>}}
  ],
  "found_keywords": [<array of matched keyword strings, max 15>],
  "missing_keywords": [<array of important missing keyword strings, max 12>],
  "suggestions": [
    {{"type": "tip|warn", "text": "<actionable suggestion — wrap the key term in <strong> tags>"}}
    ]
}}"""


def build_tailor_prompt(job_description: str, resume_text: str) -> str:
        return f"""You are an expert resume writer.

Rewrite the resume below for the job description. Never invent experience, skills, certifications, 
achievements, employers, metrics or technologies not present in the source resume.Incorporate relevant keywords naturally,
strengthen impact language without fabricating facts, and reorder bullet points to match the
job priorities. Preserve the resume's section structure. Return only the full tailored resume
as plain text, with no markdown fences or explanation.

RESUME TEXT:
{resume_text}

JOB DESCRIPTION:
{job_description}"""


@app.get("/")
def index():
    return send_file("ats-resume-matcher.html")


@app.post("/api/analyze")
def analyze_resume():
    if "resume" not in request.files:
        return jsonify({"error": {"message": "No resume PDF was uploaded."}}), 400

    resume_file = request.files["resume"]
    job_description = request.form.get("job_description", "").strip()

    if not resume_file or resume_file.filename == "":
        return jsonify({"error": {"message": "A PDF file is required."}}), 400

    if not job_description:
        return jsonify({"error": {"message": "Job description is required."}}), 400

    if not resume_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": {"message": "Only PDF files are supported."}}), 400

    pdf_bytes = resume_file.read()
    if len(pdf_bytes) > 10 * 1024 * 1024:
        return jsonify({"error": {"message": "Resume file exceeds the 10 MB limit."}}), 400

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"error": {"message": "GOOGLE_API_KEY or GEMINI_API_KEY is not set. Add it to the .env file or your environment before running the app."}}), 500

    try:
        genai.configure(api_key=api_key)
        resume_text = extract_pdf_text(pdf_bytes)
        if not resume_text:
            return jsonify({"error": {"message": "Could not read any text from the uploaded PDF. Please upload a text-based PDF resume."}}), 400

        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content(build_prompt(job_description, resume_text))

        raw_text = getattr(response, "text", "")
        if not raw_text:
            raw_text = str(response)

        clean_content = raw_text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(clean_content)
        return jsonify(parsed)

    except Exception as exc:  # pragma: no cover - backend API errors
        app.logger.exception("Gemini API request failed")
        return jsonify({"error": {"message": str(exc)}}), 500


@app.post("/api/tailor")
def tailor_resume():
    if "resume" not in request.files:
        return jsonify({"error": {"message": "No resume PDF was uploaded."}}), 400

    resume_file = request.files["resume"]
    job_description = request.form.get("job_description", "").strip()
    if not resume_file or resume_file.filename == "":
        return jsonify({"error": {"message": "A PDF file is required."}}), 400
    if not job_description:
        return jsonify({"error": {"message": "Job description is required."}}), 400
    if not resume_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": {"message": "Only PDF files are supported."}}), 400

    pdf_bytes = resume_file.read()
    if len(pdf_bytes) > 10 * 1024 * 1024:
        return jsonify({"error": {"message": "Resume file exceeds the 10 MB limit."}}), 400

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"error": {"message": "GOOGLE_API_KEY or GEMINI_API_KEY is not set."}}), 500

    try:
        genai.configure(api_key=api_key)
        resume_text = extract_pdf_text(pdf_bytes)
        if not resume_text:
            return jsonify({"error": {"message": "Could not read any text from the uploaded PDF."}}), 400

        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content(build_tailor_prompt(job_description, resume_text))
        tailored_resume = getattr(response, "text", "") or str(response)
        tailored_resume = tailored_resume.replace("```text", "").replace("```", "").strip()
        return jsonify({"tailored_resume": tailored_resume})
    except Exception as exc:  # pragma: no cover - backend API errors
        app.logger.exception("Gemini tailoring request failed")
        return jsonify({"error": {"message": str(exc)}}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
