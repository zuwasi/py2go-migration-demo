"""Example domain models — replace with your actual Python source."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Repository:
    """A code repository that has been indexed."""

    id: str
    url: str
    name: str
    branch: str = "main"
    indexed_at: Optional[datetime] = None

    def is_indexed(self) -> bool:
        return self.indexed_at is not None


@dataclass
class Enrichment:
    """An enriched code chunk with embedding and metadata."""

    id: str
    repository_id: str
    file_path: str
    content: str
    embedding: list[float] = field(default_factory=list)
    language: str = "unknown"

    def has_embedding(self) -> bool:
        return len(self.embedding) > 0


@dataclass
class SearchResult:
    """A single search result with relevance score."""

    enrichment: Enrichment
    score: float
    source: str  # "bm25" or "vector" or "fused"

    @property
    def is_relevant(self) -> bool:
        return self.score > 0.5


# --- DEPRECATED: Do not migrate ---
# This was the old snippets model, merged into Enrichment.
# Left here to demonstrate phantom feature detection.

@dataclass
class Snippet:
    """DEPRECATED — merged into Enrichment. Do not use."""

    id: str
    content: str
    repository_id: str
    line_start: int
    line_end: int
