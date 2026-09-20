from abc import ABC, abstractmethod

from app.models.job import Job


class JobSource(ABC):

    @abstractmethod
    def search(self) -> list[Job]:
        """Return normalized jobs from a job source."""
        raise NotImplementedError
