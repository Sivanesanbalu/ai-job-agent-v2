from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from app.config import RESUME_PATH


class ResumeIntelligence:
    """
    Resume = source of truth.

    Extracts candidate information without inventing credentials.
    """

    SKILL_ALIASES = {
        "Python": ["python"],
        "Generative AI": ["generative ai", "genai"],
        "LLMs": [
            "llm",
            "llms",
            "large language model",
            "large language models",
        ],
        "RAG": [
            "rag",
            "retrieval augmented generation",
            "retrieval-augmented generation",
        ],
        "AI Agents": [
            "ai agent",
            "ai agents",
            "agentic ai",
            "agentic systems",
        ],
        "Prompt Engineering": [
            "prompt engineering",
            "prompt engineer",
            "prompt design",
        ],
        "LangChain": ["langchain"],
        "LangGraph": ["langgraph"],
        "PyTorch": ["pytorch"],
        "Hugging Face": [
            "hugging face",
            "huggingface",
        ],
        "FAISS": ["faiss"],
        "FastAPI": ["fastapi"],
        "Docker": ["docker"],
        "SQL": ["sql"],
        "NLP": [
            "nlp",
            "natural language processing",
        ],
        "Computer Vision": [
            "computer vision",
            "opencv",
        ],
        "Embeddings": ["embeddings"],
        "Fine-tuning": [
            "fine-tuning",
            "fine tuning",
        ],
        "AI Automation": [
            "ai automation",
        ],
        "Machine Learning": [
            "machine learning",
            "ml",
        ],
        "Deep Learning": [
            "deep learning",
        ],
        "Scikit-learn": [
            "scikit-learn",
            "sklearn",
        ],
        "Pandas": ["pandas"],
        "NumPy": ["numpy"],
        "REST APIs": [
            "rest api",
            "rest apis",
        ],
        "Git": ["git"],
        "GitHub": ["github"],
        "Streamlit": ["streamlit"],
        "Firebase": ["firebase"],
        "AWS": ["aws"],
    }

    ROLE_TERMS = [
        "AI Engineer",
        "Artificial Intelligence Engineer",
        "Generative AI Engineer",
        "GenAI Engineer",
        "LLM Engineer",
        "AI Agent Engineer",
        "AI Automation Engineer",
        "Prompt Engineer",
        "Python AI Engineer",
        "Machine Learning Engineer",
        "ML Engineer",
        "Data Scientist",
        "NLP Engineer",
        "Computer Vision Engineer",
        "AI Developer",
        "AI Software Engineer",
        "AI Application Engineer",
        "AI Solutions Engineer",
        "AI Platform Engineer",
        "Machine Learning Developer",
        "LLM Developer",
        "GenAI Developer",
    ]

    def __init__(
        self,
        resume_path: str | None = None,
    ):
        self.resume_path = Path(
            resume_path or RESUME_PATH
        )

    def extract_text(self) -> str:
        if not self.resume_path.exists():
            cached_file = Path("data/resume_profile.json")
            if cached_file.exists():
                data = json.loads(cached_file.read_text(encoding="utf-8"))
                return data.get("raw_text", " ".join(data.get("skills", [])))
            raise FileNotFoundError(
                f"Resume not found: {self.resume_path}"
            )

        reader = PdfReader(
            str(self.resume_path)
        )

        pages = []

        for page in reader.pages:
            text = page.extract_text() or ""

            if text.strip():
                pages.append(text)

        result = "\n".join(pages)

        if not result.strip():
            raise ValueError(
                "Resume PDF has no extractable text."
            )

        return self.normalize(result)

    @staticmethod
    def normalize(text: str) -> str:
        text = text.replace(
            "\u00a0",
            " ",
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    def extract_email(
        self,
        text: str,
    ) -> str | None:
        match = re.search(
            r"\b[A-Za-z0-9._%+-]+"
            r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            text,
        )

        return (
            match.group(0)
            if match
            else None
        )

    def extract_phone(
        self,
        text: str,
    ) -> str | None:
        patterns = [
            r"(?:\+91[\s-]?)?[6-9]\d{9}",
            r"(?:\+91[\s-]?)?\d{5}[\s-]\d{5}",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
            )

            if match:
                return match.group(0)

        return None

    def extract_name(
        self,
        text: str,
    ) -> str | None:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        ignored = {
            "resume",
            "cv",
            "curriculum vitae",
            "profile",
            "contact",
            "summary",
        }

        for line in lines[:20]:
            clean = re.sub(
                r"[^A-Za-z .'-]",
                "",
                line,
            ).strip()

            if not clean:
                continue

            if clean.lower() in ignored:
                continue

            words = clean.split()

            if not 2 <= len(words) <= 5:
                continue

            if all(
                re.fullmatch(
                    r"[A-Za-z][A-Za-z.'-]*",
                    word,
                )
                for word in words
            ):
                return clean

        return None

    def extract_skills(
        self,
        text: str,
    ) -> list[str]:
        lower = text.lower()
        found = []

        for canonical, aliases in (
            self.SKILL_ALIASES.items()
        ):
            if any(
                alias in lower
                for alias in aliases
            ):
                found.append(canonical)

        return found

    def extract_roles(
        self,
        text: str,
    ) -> list[str]:
        lower = text.lower()
        found = []

        for role in self.ROLE_TERMS:
            if role.lower() in lower:
                found.append(role)

        return found

    def extract_experience(
        self,
        text: str,
    ) -> float | None:
        lower = text.lower()

        # Explicit fresher/entry-level language.
        if any(
            term in lower
            for term in [
                "fresher",
                "fresh graduate",
                "recent graduate",
                "entry level",
                "entry-level",
            ]
        ):
            return 0.0

        # Handles:
        # 0-1 years
        # 0 - 1 years
        # 0 to 1 years
        # 1 year
        # 1+ years
        range_patterns = [
            r"(\d+(?:\.\d+)?)\s*"
            r"(?:-|–|to)\s*"
            r"(\d+(?:\.\d+)?)\s*years?",
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?"
            r"\s*(?:of)?\s*experience",
            r"experience\s*"
            r"(?:of|:|-)?\s*"
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
        ]

        values = []

        for pattern in range_patterns:
            for match in re.finditer(
                pattern,
                text,
                re.IGNORECASE,
            ):
                groups = match.groups()

                try:
                    if len(groups) >= 2:
                        values.append(
                            float(groups[0])
                        )
                    else:
                        values.append(
                            float(groups[0])
                        )
                except (
                    TypeError,
                    ValueError,
                ):
                    pass

        if values:
            return min(values)

        # Resume with internships/projects but no
        # professional-years statement should be treated
        # as entry-level rather than unknown.
        lower = text.lower()

        if any(
            term in lower
            for term in [
                "internship",
                "intern",
                "apprentice",
                "trainee",
                "b.tech",
                "btech",
                "bachelor",
                "diploma",
            ]
        ):
            return 0.0

        return None

    def extract_education(
        self,
        text: str,
    ) -> list[str]:
        patterns = [
            r"B\.?\s*Tech[^.\n]{0,180}",
            r"BTech[^.\n]{0,180}",
            r"B\.?\s*E\.?[^.\n]{0,180}",
            r"Diploma[^.\n]{0,180}",
            r"Bachelor[^.\n]{0,180}",
            r"M\.?\s*Tech[^.\n]{0,180}",
            r"Master[^.\n]{0,180}",
        ]

        found = []

        for pattern in patterns:
            for match in re.finditer(
                pattern,
                text,
                re.IGNORECASE,
            ):
                value = " ".join(
                    match.group(0).split()
                )

                if value not in found:
                    found.append(value)

        return found[:10]

    def extract_certifications(
        self,
        text: str,
    ) -> list[str]:
        known = [
            "IBM AI Engineering Professional Certificate",
            "AWS AI Practitioner",
            "Coursera",
            "Forage",
            "Udacity",
            "LinkedIn Learning",
        ]

        lower = text.lower()

        return [
            item
            for item in known
            if item.lower() in lower
        ]

    def extract_locations(
        self,
        text: str,
    ) -> list[str]:
        known = [
            "Coimbatore",
            "Chennai",
            "Bengaluru",
            "Bangalore",
            "Hyderabad",
            "Pune",
            "Gurugram",
            "Gurgaon",
            "Gujarat",
            "Tamil Nadu",
            "India",
        ]

        lower = text.lower()

        return [
            item
            for item in known
            if item.lower() in lower
        ]

    def build_profile(
        self,
    ) -> dict[str, Any]:
        text = self.extract_text()

        profile = {
            "source": "resume",
            "resume_path": str(
                self.resume_path
            ),
            "name": self.extract_name(text),
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "skills": self.extract_skills(text),
            "roles": self.extract_roles(text),
            "experience_years": self.extract_experience(
                text
            ),
            "education": self.extract_education(
                text
            ),
            "certifications": self.extract_certifications(
                text
            ),
            "locations": self.extract_locations(
                text
            ),
            "projects": [
                "Eco-Transformers: AI Environmental Intelligence",
                "Autonomous AI Job Application Agent",
            ],
            "raw_text": text,
        }

        return profile

    def save_profile(
        self,
        profile: dict[str, Any],
        path: str = "data/resume_profile.json",
    ) -> Path:
        output = Path(path)

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_text(
            json.dumps(
                profile,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return output


def load_resume_profile() -> dict[str, Any]:
    cached = Path("data/resume_profile.json")
    if cached.exists():
        try:
            data = json.loads(cached.read_text(encoding="utf-8"))
            if "projects" not in data:
                data["projects"] = ["Eco-Transformers (Final Year Project)", "AI Agent Automation System"]
            return data
        except Exception:
            pass
    return ResumeIntelligence().build_profile()
