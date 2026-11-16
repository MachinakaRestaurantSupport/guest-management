"""FastAPI application entrypoint for the guest-management service."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from guest_management.models import (
    Guest,
    GuestCreate,
    GuestPointsAdjustRequest,
    Table,
    TableCreate,
    TableOccupyRequest,
)
from guest_management.store import (
    BusinessValidationError,
    InMemoryStore,
    InvalidStateTransitionError,
    NotFoundError,
)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application with an isolated in-memory store."""
    application = FastAPI(title="guest-management", version="0.1.0")
    store = InMemoryStore()

    @application.exception_handler(NotFoundError)
    async def handle_not_found(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @application.exception_handler(InvalidStateTransitionError)
    async def handle_invalid_transition(
        _: Request, exc: InvalidStateTransitionError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @application.exception_handler(BusinessValidationError)
    async def handle_business_validation(_: Request, exc: BusinessValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": str(exc)},
        )

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "guest-management"}

    @application.post("/tables", response_model=Table, status_code=status.HTTP_201_CREATED)
    def create_table(payload: TableCreate) -> Table:
        return store.create_table(table_number=payload.table_number, capacity=payload.capacity)

    @application.get("/tables", response_model=list[Table])
    def list_tables() -> list[Table]:
        return store.list_tables()

    @application.get("/tables/{table_id}", response_model=Table)
    def get_table(table_id: str) -> Table:
        return store.get_table(table_id)

    @application.post("/tables/{table_id}/occupy", response_model=Table)
    def occupy_table(table_id: str, payload: TableOccupyRequest) -> Table:
        return store.occupy_table(table_id=table_id, party_size=payload.party_size)

    @application.post("/tables/{table_id}/request-cleaning", response_model=Table)
    def request_cleaning(table_id: str) -> Table:
        return store.request_cleaning(table_id)

    @application.post("/tables/{table_id}/release", response_model=Table)
    def release_table(table_id: str) -> Table:
        return store.release_table(table_id)

    @application.post("/guests", response_model=Guest, status_code=status.HTTP_201_CREATED)
    def create_guest(payload: GuestCreate) -> Guest:
        return store.create_guest(name=payload.name, email=payload.email)

    @application.post("/guests/{guest_id}/points", response_model=Guest)
    def adjust_guest_points(guest_id: str, payload: GuestPointsAdjustRequest) -> Guest:
        return store.adjust_guest_points(guest_id=guest_id, delta=payload.delta)

    return application


app = create_app()
