from pydantic import BaseModel, Field

from app.models.browser_site import BrowserSite


class BrowserSiteCapabilities(BaseModel):
    """Capabilities exposed by a browser site adapter."""

    site: BrowserSite

    supports_form_inspection: bool = True
    supports_safe_field_fill: bool = True
    supports_human_review: bool = True

    supported_fields: list[str] = Field(
        default_factory=list
    )

    requires_login: bool = False
    supports_external_application: bool = True
    submission_implemented: bool = False
