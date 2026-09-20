from enum import Enum


class JobSourceName(str, Enum):
    LINKEDIN = "linkedin"
    NAUKRI = "naukri"
    INDEED = "indeed"
    COMPANY_SITE = "company_site"
    DEMO = "demo"
    TEST = "test"
    GENERIC = "generic"
