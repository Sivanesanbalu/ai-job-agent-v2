from app.services.resume_parser import (
    extract_skills,
    extract_contact_info,
    extract_experience_years,
    extract_education,
    parse_resume,
)
from pypdf import PdfWriter
import io

def create_sample_pdf_bytes():
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()

def test_extract_skills_canonical_matching():
    sample_text = """
    Senior Software Engineer with 7 years of expertise in Python, FastAPI, Docker, and Kubernetes.
    Proficient with LangChain, PyTorch, and building RAG pipelines using Pinecone and ChromaDB.
    Frontend experience in React, Next.js, and TypeScript. Familiar with AWS and Redis.
    """
    skills = extract_skills(sample_text)
    
    assert "Python" in skills
    assert "FastAPI" in skills
    assert "Docker" in skills
    assert "Kubernetes" in skills
    assert "LangChain" in skills
    assert "PyTorch" in skills
    assert "RAG" in skills
    assert "React" in skills
    assert "Next.js" in skills
    assert "TypeScript" in skills
    assert "AWS" in skills
    assert "Redis" in skills

def test_extract_skills_boundary_precision():
    # Should not falsely match partial words (e.g. "go" in "good" or "py" in "copy")
    sample_text = "He had good intentions and made a copy of the report."
    skills = extract_skills(sample_text)
    assert "Python" not in skills

def test_extract_contact_info():
    sample_text = """
    Jane Doe
    jane.doe@example.com | +1 (555) 123-4567 | San Francisco, CA
    https://linkedin.com/in/janedoe | https://github.com/janedoe
    Summary:
    Lead AI Engineer with proven track record in deploying large scale models.
    """
    contact = extract_contact_info(sample_text)
    assert contact["email"] == "jane.doe@example.com"
    assert "123-4567" in contact["phone"]
    assert "linkedin.com/in/janedoe" in contact["linkedin_url"]
    assert "github.com/janedoe" in contact["github_url"]
    assert contact["name"] == "Jane Doe"

def test_extract_experience_years():
    text_1 = "Over 6.5 years of professional software development experience."
    years_1 = extract_experience_years(text_1)
    assert years_1 == 6.5

    text_2 = "8+ years building enterprise web applications."
    years_2 = extract_experience_years(text_2)
    assert years_2 == 8.0

    text_3 = "Recent graduate looking for entry level opportunities."
    years_3 = extract_experience_years(text_3)
    assert years_3 == 1.0

def test_parse_resume_fallback_pipeline():
    sample_text = """
    Alex Rivera
    alex.rivera@testmail.com | 9876543210
    Bangalore, India
    
    Professional Summary:
    Full Stack Developer with 4 years of experience specializing in Python, Django, React, and PostgreSQL.
    
    Education:
    Bachelor of Technology in Computer Science, 2020
    """
    skills = extract_skills(sample_text)
    contacts = extract_contact_info(sample_text)
    exp = extract_experience_years(sample_text)
    edu = extract_education(sample_text)

    assert "Python" in skills
    assert "React" in skills
    assert "PostgreSQL" in skills or "SQL" in skills
    assert contacts["email"] == "alex.rivera@testmail.com"
    assert exp == 4.0
    assert "Computer Science" in edu

    # Also test parse_resume file runner with pdf bytes
    pdf_bytes = create_sample_pdf_bytes()
    parsed = parse_resume(pdf_bytes, "sample.pdf")
    assert isinstance(parsed, dict)
    assert "skills" in parsed
    assert "projects" in parsed
