"""HTTP routes for the price-comparison API."""

from fastapi import APIRouter, HTTPException

from api import jobs
from api.schemas import JobResponse, SearchRequest, SearchResponse

router = APIRouter()


@router.post("/api/search", response_model=SearchResponse, status_code=202)
async def create_search(body: SearchRequest) -> SearchResponse:
    """Start (or dedupe) a price-comparison search."""
    job_id = jobs.create_job(body.query, body.location)
    return SearchResponse(job_id=job_id)


@router.get("/api/search/{job_id}", response_model=JobResponse)
async def get_search(job_id: str) -> JobResponse:
    """Return the current state of a search job."""
    job = jobs.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(**job.to_dict())


@router.post(
    "/api/search/{job_id}/refresh", response_model=SearchResponse, status_code=202
)
async def refresh_search(job_id: str) -> SearchResponse:
    """Start a new job for the same query/location, bypassing the cache."""
    job = jobs.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    new_id = jobs.create_job(job.query, job.location, force_refresh=True)
    return SearchResponse(job_id=new_id)
