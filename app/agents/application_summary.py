from app.data.candidate_profile import CANDIDATE_PROFILE
from app.models.job import Job


SKILL_ALIASES = {
    "llms": [
        "llm",
        "llms",
        "large language model",
        "large language models",
    ],
    "rag": [
        "rag",
        "retrieval augmented generation",
        "retrieval-augmented generation",
    ],
    "generative ai": [
        "generative ai",
        "genai",
        "generative artificial intelligence",
    ],
    "ai agents": [
        "ai agents",
        "ai agent",
        "agentic ai",
        "agentic systems",
    ],
    "prompt engineering": [
        "prompt engineering",
        "prompt engineer",
        "prompt design",
    ],
}


CANONICAL_SKILL_NAMES = {
    "python": "Python",
    "generative ai": "Generative AI",
    "genai": "Generative AI",
    "llms": "LLMs",
    "llm": "LLMs",
    "rag": "RAG",
    "ai agents": "AI Agents",
    "ai agent": "AI Agents",
    "prompt engineering": "Prompt Engineering",
    "langchain": "LangChain",
    "langgraph": "LangGraph",
    "pytorch": "PyTorch",
    "hugging face": "Hugging Face",
    "faiss": "FAISS",
    "fastapi": "FastAPI",
    "docker": "Docker",
    "sql": "SQL",
    "nlp": "NLP",
    "computer vision": "Computer Vision",
    "embeddings": "Embeddings",
    "fine-tuning": "Fine-tuning",
    "ai automation": "AI Automation",
}


def normalize_skill_name(skill: str) -> str:
    skill_clean = " ".join(skill.split()).strip()
    skill_lower = skill_clean.lower()

    return CANONICAL_SKILL_NAMES.get(
        skill_lower,
        skill_clean,
    )


def skill_matches(skill: str, job_text: str) -> bool:
    skill_lower = skill.lower()

    aliases = SKILL_ALIASES.get(
        skill_lower,
        [skill_lower],
    )

    return any(
        alias in job_text
        for alias in aliases
    )


def generate_application_summary(job: Job) -> dict:
    job_text = f"{job.title} {job.description}".lower()

    matched_skills = [
        normalize_skill_name(skill)
        for skill in CANDIDATE_PROFILE.skills
        if skill_matches(skill, job_text)
    ]

    return {
        "job_title": job.title,
        "company": job.company,
        "match_score": job.match_score,
        "matched_candidate_skills": matched_skills,
        "candidate_headline": CANDIDATE_PROFILE.headline,
        "education": CANDIDATE_PROFILE.education,
        "notice_period_days": CANDIDATE_PROFILE.notice_period_days,
    }
