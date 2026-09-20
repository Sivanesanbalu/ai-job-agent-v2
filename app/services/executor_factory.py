from app.config import APPLICATION_EXECUTOR
from app.services.application_executor_base import ApplicationExecutor
from app.services.browser_executor import BrowserExecutor
from app.services.demo_executor import DemoExecutor


def get_application_executor() -> ApplicationExecutor:
    if APPLICATION_EXECUTOR == "demo":
        return DemoExecutor()

    if APPLICATION_EXECUTOR == "browser":
        return BrowserExecutor()

    raise ValueError(
        f"Unsupported application executor: "
        f"{APPLICATION_EXECUTOR}"
    )
