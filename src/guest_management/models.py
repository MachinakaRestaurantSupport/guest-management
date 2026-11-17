"""Domain and API schema models for the guest-management service."""

from typing import Literal

from pydantic import BaseModel, Field

TableStatus = Literal["available", "occupied", "cleaning"]


class TableCreate(BaseModel):
    """Request payload for creating a table."""

    table_number: str = Field(min_length=1)
    capacity: int = Field(gt=0)


class TableOccupyRequest(BaseModel):
    """Request payload for occupying a table."""

    party_size: int = Field(gt=0)


class Table(BaseModel):
    """Table resource representation."""

    id: str
    table_number: str
    capacity: int
    status: TableStatus = "available"
    current_session_id: str | None = None
    qr_token: str | None = None


class GuestCreate(BaseModel):
    """Request payload for registering a guest."""

    name: str = Field(min_length=1)
    email: str | None = None


class GuestPointsAdjustRequest(BaseModel):
    """Request payload for adjusting guest loyalty points."""

    delta: int


class Guest(BaseModel):
    """Guest resource representation."""

    id: str
    name: str
    email: str | None = None
    points: int = 0
