from __future__ import annotations

import io
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests
from pypdf import PdfReader
import docx
from app.core.config import settings

logger = logging.getLogger(__name__)

SKILL_CATALOG = {
    # AI / ML / Data Science
    "Python": ["python", "py"],
    "Generative AI": ["generative ai", "genai", "gen ai"],
    "Large Language Models (LLMs)": ["llm", "llms", "large language model", "large language models"],
    "RAG": ["rag", "retrieval augmented generation", "retrieval-augmented generation"],
    "AI Agents": ["ai agent", "ai agents", "agentic ai", "agentic systems"],
    "Prompt Engineering": ["prompt engineering", "prompt engineer", "prompt design"],
    "LangChain": ["langchain"],
    "LangGraph": ["langgraph"],
    "LlamaIndex": ["llamaindex", "llama-index"],
    "PyTorch": ["pytorch", "torch"],
    "TensorFlow": ["tensorflow", "tf"],
    "Hugging Face": ["hugging face", "huggingface", "transformers"],
    "FAISS": ["faiss"],
    "ChromaDB": ["chromadb", "chroma"],
    "Pinecone": ["pinecone"],
    "Qdrant": ["qdrant"],
    "Weaviate": ["weaviate"],
    "OpenAI API": ["openai", "gpt-4", "gpt-3.5"],
    "Ollama": ["ollama"],
    "NLP": ["nlp", "natural language processing"],
    "Computer Vision": ["computer vision", "opencv", "cv"],
    "Embeddings": ["embeddings", "vector search"],
    "Fine-tuning": ["fine-tuning", "fine tuning", "lora", "qlora"],
    "Machine Learning": ["machine learning", "ml", "scikit-learn", "sklearn"],
    "Deep Learning": ["deep learning", "neural networks"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],

    # Backend / Engineering
    "FastAPI": ["fastapi"],
    "Flask": ["flask"],
    "Django": ["django"],
    "REST APIs": ["rest api", "rest apis", "restful"],
    "GraphQL": ["graphql"],
    "Node.js": ["nodejs", "node.js", "node"],
    "SQL": ["sql", "postgresql", "postgres", "mysql", "sqlite"],
    "MongoDB": ["mongodb", "mongo"],
    "Redis": ["redis"],
    "Docker": ["docker", "containerization"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Git": ["git", "github", "gitlab"],
    "Linux": ["linux", "bash", "shell"],
    "AWS": ["aws", "amazon web services", "s3", "ec2", "lambda"],
    "GCP": ["gcp", "google cloud"],
    "Azure": ["azure"],

    # Frontend
    "React": ["react", "react.js", "reactjs"],
    "Next.js": ["next.js", "nextjs"],
    "TypeScript": ["typescript", "ts"],
    "JavaScript": ["javascript", "js"],
    "Tailwind CSS": ["tailwind", "tailwindcss"],
    "HTML/CSS": ["html", "css", "html5", "css3"],
}


def extract_text_from_pdf(file_path_or_bytes: str | Path | bytes) -> str:
    if isinstance(file_path_or_bytes, (str, Path)):
        reader = PdfReader(str(file_path_or_bytes))
    else:
        reader = PdfReader(io.BytesIO(file_path_or_bytes))

    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_parts.append(page_text)
    return "\n".join(text_parts).strip()


def extract_text_from_docx(file_path_or_bytes: str | Path | bytes) -> str:
    if isinstance(file_path_or_bytes, (str, Path)):
        doc = docx.Document(str(file_path_or_bytes))
    else:
        doc = docx.Document(io.BytesIO(file_path_or_bytes))

    text_parts = []
    for paragraph in doc.paragraphs:
        if paragraph.text:
            text_parts.append(paragraph.text)
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                text_parts.append(row_text)
    return "\n".join(text_parts).strip()


def extract_text(file_path_or_bytes: str | Path | bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path_or_bytes)
    elif ext in {".docx", ".doc"}:
        return extract_text_from_docx(file_path_or_bytes)
    raise ValueError(f"Unsupported file type: {ext}")


def extract_skills(text: str) -> List[str]:
    lowered = f" {text.lower()} "
    found_skills = []
    for canonical_name, aliases in SKILL_CATALOG.items():
        for alias in aliases:
            # Pattern match with word boundary
            pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
            if re.search(pattern, lowered):
                found_skills.append(canonical_name)
                break
    return found_skills


def extract_contact_info(text: str) -> Dict[str, Any]:
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Name heuristic: Usually in first 3 lines
    name = ""
    for line in lines[:4]:
        # Filter out email, phone, url lines
        if "@" in line or "http" in line or "linkedin" in line or "github" in line:
            continue
        cleaned = re.sub(r"[^a-zA-Z\s\.]", "", line).strip()
        if 2 <= len(cleaned.split()) <= 4 and len(cleaned) < 50:
            name = cleaned
            break

    # Email
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    email = email_match.group(0) if email_match else ""

    # Phone
    phone_match = re.search(
        r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}",
        text,
    )
    phone = phone_match.group(0).strip() if phone_match else ""

    # LinkedIn
    linkedin_match = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+",
        text,
        re.IGNORECASE,
    )
    linkedin_url = linkedin_match.group(0) if linkedin_match else ""
    if linkedin_url and not linkedin_url.startswith("http"):
        linkedin_url = f"https://{linkedin_url}"

    # GitHub
    github_match = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/[\w\-]+",
        text,
        re.IGNORECASE,
    )
    github_url = github_match.group(0) if github_match else ""
    if github_url and not github_url.startswith("http"):
        github_url = f"https://{github_url}"

    # Location (detect common Indian cities or generic words)
    cities = [
        "Bangalore", "Bengaluru", "Chennai", "Coimbatore", "Hyderabad",
        "Pune", "Mumbai", "Delhi", "Gurugram", "Gurgaon", "Noida",
        "Kolkata", "Ahmedabad", "Kochi", "Trivandrum",
    ]
    location = ""
    for city in cities:
        if re.search(r"\b" + re.escape(city) + r"\b", text, re.IGNORECASE):
            location = city
            break

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin_url": linkedin_url,
        "github_url": github_url,
        "location": location,
    }


def extract_education(text: str) -> str:
    degrees = [
        "B.Tech", "B.E.", "Bachelor of Technology", "Bachelor of Engineering",
        "M.Tech", "M.E.", "Master of Technology", "M.S.", "B.S.", "B.Sc", "M.Sc",
        "BCA", "MCA", "Ph.D", "Doctor of Philosophy",
    ]
    for degree in degrees:
        match = re.search(
            re.escape(degree) + r"[^\n,\.;]*",
            text,
            re.IGNORECASE,
        )
        if match:
            return match.group(0).strip()
    return "Bachelor's Degree in Computer Science / Technology"


def extract_experience_years(text: str) -> float:
    # Look for explicit statements e.g. "X years of experience"
    match = re.search(
        r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)\b",
        text,
        re.IGNORECASE,
    )
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass

    # Look for date ranges e.g. 2022 - 2024
    years = [int(y) for y in re.findall(r"\b(20\d\d)\b", text)]
    if len(years) >= 2:
        span = max(years) - min(years)
        if 0 < span <= 30:
            return float(span)

    return 1.0


def enrich_with_ai(raw_text: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Call Ollama if available to refine extracted fields, or fallback cleanly."""
    if not settings.OLLAMA_MODEL:
        return parsed

    prompt = f"""You are a resume parsing assistant. Extract structured candidate information in JSON format from the following resume text:
{raw_text[:3000]}

Return ONLY a valid JSON object with the following keys:
{{
    "name": "full name",
    "headline": "professional headline",
    "summary": "1-2 sentence professional summary",
    "skills": ["list", "of", "skills"],
    "education": "degree and university",
    "experience_years": 1.5,
    "projects": [{"title": "project name", "description": "short description"}]
}}
"""
    try:
        res = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=10,
        )
        if res.ok:
            data = res.json().get("response")
            enriched = json.loads(data)
            for k, v in enriched.items():
                if v and not parsed.get(k):
                    parsed[k] = v
    except Exception as e:
        logger.debug(f"AI enrichment skipped or failed: {e}")

    return parsed


def parse_resume(file_path_or_bytes: str | Path | bytes, filename: str) -> Dict[str, Any]:
    raw_text = extract_text(file_path_or_bytes, filename)
    contacts = extract_contact_info(raw_text)
    skills = extract_skills(raw_text)
    education = extract_education(raw_text)
    experience_years = extract_experience_years(raw_text)

    # First name / last name split
    full_name = contacts.get("name", "")
    parts = full_name.split()
    first_name = parts[0] if parts else ""
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    parsed: Dict[str, Any] = {
        "name": full_name,
        "first_name": first_name,
        "last_name": last_name,
        "email": contacts.get("email", ""),
        "phone": contacts.get("phone", ""),
        "location": contacts.get("location", ""),
        "linkedin_url": contacts.get("linkedin_url", ""),
        "github_url": contacts.get("github_url", ""),
        "portfolio_url": "",
        "headline": f"{skills[0]} Specialist" if skills else "Software Professional",
        "summary": raw_text[:300].replace("\n", " ").strip() if raw_text else "",
        "skills": skills,
        "education": education,
        "experience_years": experience_years,
        "projects": [],
        "raw_text_length": len(raw_text),
    }

    # Attempt AI enrichment if Ollama is available
    parsed = enrich_with_ai(raw_text, parsed)
    return parsed
