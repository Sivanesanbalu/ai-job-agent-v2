# ============================================================
# AI JOB AGENT V2 — JOB SEARCH & APPLICATION CONFIGURATION
# ============================================================

# ------------------------------------------------------------
# Target Roles
# ------------------------------------------------------------

ROLES = [
    "AI Engineer",
    "Generative AI Engineer",
    "GenAI Engineer",
    "LLM Engineer",
    "AI Automation Engineer",
    "AI Agent Engineer",
    "Prompt Engineer",
    "Python AI Engineer",
    "Machine Learning Engineer",
    "Junior Machine Learning Engineer",
]


# ------------------------------------------------------------
# Preferred Locations
# ------------------------------------------------------------

LOCATIONS = [
    "Coimbatore",
    "Chennai",
    "Bengaluru",
    "Bangalore",
    "Hyderabad",
    "Pune",
    "Gurugram",
    "Gurgaon",
    "Gujarat",
]


# ------------------------------------------------------------
# Job Filters
# ------------------------------------------------------------

# Candidate is targeting fresher / junior opportunities.
MIN_EXPERIENCE_YEARS = 0
MAX_EXPERIENCE_YEARS = 1

# Minimum expected salary.
MIN_SALARY_LPA = 5.0

# Minimum AI-job match score.
MIN_MATCH_SCORE = 70


# ------------------------------------------------------------
# Application Limits
# ------------------------------------------------------------

# Consider all matching jobs discovered by the agent.
# The agent should still deduplicate jobs and reject jobs
# that do not satisfy the configured filters.

MAX_APPLICATIONS_PER_DAY = None


# ------------------------------------------------------------
# Application Behaviour
# ------------------------------------------------------------

# User requested automatic submission without a confirmation
# step.
AUTO_SUBMIT = True

# No manual review gate before submission.
REQUIRE_HUMAN_REVIEW = False

APPLICATION_EXECUTOR = "browser"


# ------------------------------------------------------------
# Human/Security Boundaries
# ------------------------------------------------------------

# Never attempt to bypass CAPTCHA, OTP, MFA, Cloudflare,
# anti-bot challenges, or other security verification.
ALLOW_SECURITY_BYPASS = False

# If a security/identity verification step appears, stop and
# return the application to the user instead of attempting
# to bypass it.
STOP_ON_SECURITY_CHALLENGE = True


# ------------------------------------------------------------
# Application Assets
# ------------------------------------------------------------

# Set these to the actual files you want the browser agent
# to use when an application asks for them.
#
# Example:
# RESUME_PATH = "/Users/sivanesanbalu/Documents/resume.pdf"
# PHOTO_PATH = "/Users/sivanesanbalu/Documents/photo.jpg"

RESUME_PATH = "/Users/sivanesanbalu/Downloads/package121/data/resumes/Sivanesan_B_AI_Engineer_Resume.pdf"
PHOTO_PATH = None


# ------------------------------------------------------------
# Standard Application Answers
# ------------------------------------------------------------

APPLICATION_ANSWERS = {
    # Use only when the application asks the corresponding
    # question and the answer is explicitly configured.

    "country": "India",

    # User requested this standard answer.
    "disability": "No",

    # Actual experience should remain grounded in the resume/
    # candidate profile. Do not fabricate experience.
    "experience_range": "0-1 years",
}


# ------------------------------------------------------------
# Application Field Policy
# ------------------------------------------------------------

# Automatically fill only fields for which the agent has
# explicit candidate data or configured application data.

SAFE_AUTO_FILL_FIELDS = [
    "name",
    "first_name",
    "last_name",
    "email",
    "cover_letter",
]

# Human-supplied values can be used for fields that aren't
# stored as automatic profile data.
HUMAN_INPUT_FIELDS = [
    "phone",
]


# ------------------------------------------------------------
# Submission Policy
# ------------------------------------------------------------

# The agent can proceed automatically after all required
# application fields have valid candidate/configured data.

REQUIRE_EXPLICIT_SUBMISSION_CONFIRMATION = False
