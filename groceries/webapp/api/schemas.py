"""Pydantic request/response models for the price-comparison API."""

from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    """Body of POST /api/search."""

    query: str
    location: str

    @field_validator("query", "location")
    @classmethod
    def _must_be_non_empty(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must be a non-empty string")
        return stripped


class SearchResponse(BaseModel):
    """202 response containing the new (or deduped) job id."""

    job_id: str


class StoreStatusResponse(BaseModel):
    """Per-store status within a job."""

    name: str
    status: str
    product_count: int = 0
    error: str | None = None
    cached: bool = False


class ScoreboardResponse(BaseModel):
    """Aggregate wins per store and total ties."""

    wins: dict[str, int] = Field(default_factory=dict)
    ties: int = 0


class ProductPrice(BaseModel):
    """A single store's price entry for a product row."""

    store: str
    sale_price: str
    parsed_price: float | None = None
    original_price: str | None = None
    image_url: str
    is_best: bool = False
    delta: float | None = None


class ProductRow(BaseModel):
    """A matched product across one or more stores."""

    display_name: str
    brand: str = ""
    confidence: str
    tag: str = ""
    winner: str | None = None
    only_store: str | None = None
    prices: list[ProductPrice] = Field(default_factory=list)


class JobResponse(BaseModel):
    """Full job state, matching the API contract shape."""

    id: str
    status: str
    query: str
    location: str
    inferred_category: str | None = None
    generated_at: str | None = None
    cached: bool = False
    error: str | None = None
    stores: list[StoreStatusResponse] = Field(default_factory=list)
    scoreboard: ScoreboardResponse = Field(default_factory=ScoreboardResponse)
    products: list[ProductRow] = Field(default_factory=list)
