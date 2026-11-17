"""In-memory data store and domain transition logic for guest-management."""

import secrets
from uuid import uuid4

from guest_management.models import Guest, Table


class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""


class InvalidStateTransitionError(Exception):
    """Raised when an operation is invalid for the current table status."""


class BusinessValidationError(Exception):
    """Raised when a domain constraint such as capacity or point balance fails."""


class InMemoryStore:
    """In-memory repository for tables and guests."""

    def __init__(self) -> None:
        self._tables: dict[str, Table] = {}
        self._guests: dict[str, Guest] = {}

    def create_table(self, table_number: str, capacity: int) -> Table:
        """Register a new table in the available state."""
        table = Table(
            id=str(uuid4()),
            table_number=table_number,
            capacity=capacity,
            status="available",
            current_session_id=None,
            qr_token=None,
        )
        self._tables[table.id] = table
        return table

    def list_tables(self) -> list[Table]:
        """Return all registered tables."""
        return list(self._tables.values())

    def get_table(self, table_id: str) -> Table:
        """Return a table by ID or raise NotFoundError."""
        table = self._tables.get(table_id)
        if table is None:
            raise NotFoundError(f"Table '{table_id}' not found")
        return table

    def occupy_table(self, table_id: str, party_size: int) -> Table:
        """Transition an available table to occupied and issue session/QR tokens."""
        table = self.get_table(table_id)
        if table.status != "available":
            raise InvalidStateTransitionError(
                f"Cannot occupy table '{table_id}' in status '{table.status}'"
            )
        if party_size > table.capacity:
            raise BusinessValidationError(
                f"Party size {party_size} exceeds table capacity {table.capacity}"
            )
        updated = table.model_copy(
            update={
                "status": "occupied",
                "current_session_id": str(uuid4()),
                "qr_token": secrets.token_urlsafe(16),
            }
        )
        self._tables[table_id] = updated
        return updated

    def request_cleaning(self, table_id: str) -> Table:
        """Transition an occupied table to cleaning and clear active session data."""
        table = self.get_table(table_id)
        if table.status != "occupied":
            raise InvalidStateTransitionError(
                f"Cannot request cleaning for table '{table_id}' in status '{table.status}'"
            )
        updated = table.model_copy(
            update={
                "status": "cleaning",
                "current_session_id": None,
                "qr_token": None,
            }
        )
        self._tables[table_id] = updated
        return updated

    def release_table(self, table_id: str) -> Table:
        """Transition a cleaning table back to available."""
        table = self.get_table(table_id)
        if table.status != "cleaning":
            raise InvalidStateTransitionError(
                f"Cannot release table '{table_id}' in status '{table.status}'"
            )
        updated = table.model_copy(update={"status": "available"})
        self._tables[table_id] = updated
        return updated

    def create_guest(self, name: str, email: str | None = None) -> Guest:
        """Register a new guest with zero initial points."""
        guest = Guest(
            id=str(uuid4()),
            name=name,
            email=email,
            points=0,
        )
        self._guests[guest.id] = guest
        return guest

    def list_guests(self) -> list[Guest]:
        """Return all registered guests."""
        return list(self._guests.values())

    def adjust_guest_points(self, guest_id: str, delta: int) -> Guest:
        """Add or subtract points for a guest, rejecting negative balances."""
        guest = self._guests.get(guest_id)
        if guest is None:
            raise NotFoundError(f"Guest '{guest_id}' not found")
        new_points = guest.points + delta
        if new_points < 0:
            raise BusinessValidationError(
                f"Insufficient points: current={guest.points}, delta={delta}"
            )
        updated = guest.model_copy(update={"points": new_points})
        self._guests[guest_id] = updated
        return updated
