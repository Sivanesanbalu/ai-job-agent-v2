from enum import Enum


class BrowserSite(str, Enum):
    LINKEDIN = "linkedin"
    NAUKRI = "naukri"
    INDEED = "indeed"
    GENERIC = "generic"
