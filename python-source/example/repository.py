"""Example repository layer — replace with your actual Python source."""

from abc import ABC, abstractmethod
from typing import Optional

from .models import Repository, Enrichment, SearchResult


class BaseRepository(ABC):
    """Abstract repository interface."""

    @abstractmethod
    def get_repository(self, repo_id: str) -> Optional[Repository]:
        ...

    @abstractmethod
    def list_repositories(self) -> list[Repository]:
        ...

    @abstractmethod
    def save_enrichment(self, enrichment: Enrichment) -> None:
        ...

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        ...


class PostgresRepository(BaseRepository):
    """PostgreSQL implementation of the repository."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        # In real code: SQLAlchemy engine setup here

    def get_repository(self, repo_id: str) -> Optional[Repository]:
        # Placeholder — your actual SQLAlchemy query
        raise NotImplementedError

    def list_repositories(self) -> list[Repository]:
        # NOTE: No pagination — this is a known issue to fix during migration
        raise NotImplementedError

    def save_enrichment(self, enrichment: Enrichment) -> None:
        raise NotImplementedError

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        raise NotImplementedError
