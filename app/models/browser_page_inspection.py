from pydantic import BaseModel, Field

from app.models.browser_page_state import BrowserPageState


class BrowserPageInspection(BaseModel):
    """Structured browser page inspection result."""

    state: BrowserPageState = BrowserPageState.UNKNOWN

    url: str = ""
    title: str = ""

    has_form: bool = False
    visible_input_count: int = 0
    visible_textarea_count: int = 0
    visible_select_count: int = 0
    visible_button_count: int = 0

    detected_signals: list[str] = Field(
        default_factory=list
    )

    requires_human_action: bool = False
