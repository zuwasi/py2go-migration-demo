"""Example FastAPI server — replace with your actual Python source."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .models import Repository, SearchResult
from .repository import BaseRepository


# --- Request / Response models ---

class SearchRequest(BaseModel):
    query: str
    limit: int = 10


class SearchResponse(BaseModel):
    results: list[dict]
    total: int


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"


# --- Application ---

def create_app(repo: BaseRepository) -> FastAPI:
    app = FastAPI(title="Kodit", version="1.0.0")

    @app.get("/health")
    def health() -> HealthResponse:
        return HealthResponse()

    @app.get("/api/v1/repositories")
    def list_repositories() -> list[dict]:
        # NOTE: No pagination — needs to be added during migration
        repos = repo.list_repositories()
        return [{"id": r.id, "name": r.name, "url": r.url} for r in repos]

    @app.post("/api/v1/search")
    def search(request: SearchRequest) -> SearchResponse:
        results = repo.search(request.query, limit=request.limit)
        return SearchResponse(
            results=[
                {"file": r.enrichment.file_path, "score": r.score}
                for r in results
            ],
            total=len(results),
        )

    return app
