from __future__ import annotations

from app.services.base_discovery import JobSource


class SourceRegistry:

    def __init__(
        self,
        sources: list[JobSource] | None = None,
    ):
        self._sources: list[JobSource] = []

        for source in sources or []:
            self.register(source)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        source: JobSource,
    ) -> None:

        if source not in self._sources:
            self._sources.append(source)

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_sources(self) -> list[JobSource]:
        return list(self._sources)

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._sources)

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def close(self) -> None:
        """
        Close sources that expose a close() method.
        """

        for source in self._sources:

            close = getattr(
                source,
                "close",
                None,
            )

            if callable(close):

                try:
                    close()

                except Exception as error:
                    print(
                        "Source close failed: "
                        f"{source.__class__.__name__}: "
                        f"{error}"
                    )
