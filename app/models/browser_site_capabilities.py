from pydantic import BaseModel, Field

from app.models.browser_site import BrowserSite


UNIVERSAL_SUPPORTED_FIELDS = [
    "name",
    "first_name",
    "last_name",
    "email",
    "phone",
    "linkedin",
    "github",
    "portfolio",
    "city",
    "state",
    "country",
    "address",
    "pincode",
    "headline",
    "current_company",
    "experience",
    "notice_period",
    "current_salary",
    "expected_salary",
    "education",
    "university",
    "work_authorization",
    "sponsorship",
    "relocation",
    "cover_letter",
]


class BrowserSiteCapabilities(BaseModel):
    """Capabilities exposed by a browser site adapter."""

    site: BrowserSite

    supports_form_inspection: bool = True
    supports_safe_field_fill: bool = True
    supports_human_review: bool = True

    supported_fields: list[str] = Field(
        default_factory=lambda: list(UNIVERSAL_SUPPORTED_FIELDS)
    )

    requires_login: bool = False
    supports_external_application: bool = True
    submission_implemented: bool = True
