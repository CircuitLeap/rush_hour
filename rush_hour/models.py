"""Data models for the Rush Hour game."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Direction(str, Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class Orientation(str, Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@dataclass(frozen=True)
class Vehicle:
    """A vehicle on the board.

    Attributes:
        id: Single-letter identifier (X = target car).
        row: Top-most row occupied (0-indexed).
        col: Left-most column occupied (0-indexed).
        length: Number of cells occupied (2 or 3).
        orientation: HORIZONTAL or VERTICAL.
    """

    id: str
    row: int
    col: int
    length: int
    orientation: Orientation

    @property
    def cells(self) -> list[tuple[int, int]]:
        """Return all (row, col) cells this vehicle occupies."""
        if self.orientation == Orientation.HORIZONTAL:
            return [(self.row, self.col + i) for i in range(self.length)]
        return [(self.row + i, self.col) for i in range(self.length)]


@dataclass(frozen=True)
class BoardState:
    """Immutable snapshot of the board.

    The vehicles tuple is sorted by id for consistent hashing/equality.
    """

    vehicles: tuple[Vehicle, ...]
    size: int = 6

    def vehicle_by_id(self, vehicle_id: str) -> Vehicle | None:
        for v in self.vehicles:
            if v.id == vehicle_id:
                return v
        return None


@dataclass(frozen=True)
class Move:
    """A move: slide vehicle_id in direction by distance cells."""

    vehicle_id: str
    direction: Direction
    distance: int = 1


@dataclass(frozen=True)
class MoveResult:
    """Result of attempting a move.

    Attributes:
        success: Whether the move was applied.
        message: Human-readable outcome description.
        move_count: Total moves made so far.
        is_solved: Whether the puzzle is now solved.
    """

    success: bool
    message: str
    move_count: int
    is_solved: bool
