from typing import Any
from pydantic import BaseModel, Field


class TravelRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User travel request prompt")
    thread_id: str | None = Field(default=None, description="Optional thread session ID")


class ApprovalRequest(BaseModel):
    thread_id: str = Field(..., min_length=1, description="Thread session ID to resume")
    approved: bool = Field(..., description="Whether user approves the draft itinerary")
    feedback: str = Field(default="", description="Optional revision instructions")


class HealthResponse(BaseModel):
    status: str
    message: str
    features: list[str]
