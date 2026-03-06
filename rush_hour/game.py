"""Core Rush Hour game engine."""

from __future__ import annotations

from rush_hour.display import render_ascii, render_json
from rush_hour.models import BoardState, Direction, Move, MoveResult, Orientation, Vehicle
from rush_hour.puzzles import get_puzzle


class RushHourGame:
    """Rush Hour sliding puzzle.

    The goal is to move the target car (X) to the right edge of the board
    (row 2, column 5). Cars slide along their orientation axis only.

    Usage::

        game = RushHourGame.from_puzzle("beginner_1")
        print(game.get_state(format="ascii"))
        result = game.move("X", "right", 1)
        print(result.message)
    """

    TARGET_ID = "X"
    EXIT_ROW = 2
    EXIT_COL = 5  # right-most column the target's tail must reach

    def __init__(self, board: BoardState) -> None:
        self._initial_board = board
        self._board = board
        self._move_count = 0

    @classmethod
    def from_puzzle(cls, puzzle_name: str) -> RushHourGame:
        """Create a game from a named puzzle.

        Args:
            puzzle_name: e.g. "beginner_1", "expert_3".

        Raises:
            ValueError: If the puzzle name is unknown.
        """
        board = get_puzzle(puzzle_name)
        return cls(board)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_state(self, format: str = "ascii") -> str | dict:
        """Return the current board state.

        Args:
            format: "ascii" for a visual grid, "json" for a structured dict.

        Returns:
            str (ascii) or dict (json).
        """
        if format == "ascii":
            return render_ascii(self._board, self._move_count)
        if format == "json":
            return render_json(self._board, self._move_count, self.is_solved())
        raise ValueError(f"Unknown format {format!r}. Use 'ascii' or 'json'.")

    def move(self, vehicle_id: str, direction: str, distance: int = 1) -> MoveResult:
        """Attempt to slide a vehicle.

        Args:
            vehicle_id: Single-letter vehicle identifier (e.g. "X", "B").
            direction: "up", "down", "left", or "right".
            distance: Number of cells to slide (1-5).

        Returns:
            MoveResult with success flag, message, move count, and solved status.
        """
        vehicle_id = vehicle_id.upper()

        # Validate direction
        try:
            dir_enum = Direction(direction.lower())
        except ValueError:
            return MoveResult(
                success=False,
                message=f"Invalid direction '{direction}'. Use: up, down, left, right.",
                move_count=self._move_count,
                is_solved=self.is_solved(),
            )

        # Validate distance
        if not isinstance(distance, int) or distance < 1 or distance > 5:
            return MoveResult(
                success=False,
                message=f"Invalid distance {distance}. Must be an integer from 1 to 5.",
                move_count=self._move_count,
                is_solved=self.is_solved(),
            )

        # Find vehicle
        vehicle = self._board.vehicle_by_id(vehicle_id)
        if vehicle is None:
            available = sorted(v.id for v in self._board.vehicles)
            return MoveResult(
                success=False,
                message=f"No vehicle '{vehicle_id}' on the board. Available: {', '.join(available)}.",
                move_count=self._move_count,
                is_solved=self.is_solved(),
            )

        # Validate direction vs orientation
        move = Move(vehicle_id, dir_enum, distance)
        if not self._direction_valid_for_vehicle(vehicle, dir_enum):
            valid = self._valid_directions(vehicle)
            return MoveResult(
                success=False,
                message=(
                    f"Vehicle '{vehicle_id}' is {vehicle.orientation.value} "
                    f"and can only move {valid[0].value}/{valid[1].value}."
                ),
                move_count=self._move_count,
                is_solved=self.is_solved(),
            )

        # Try to apply the move
        new_vehicle = self._compute_new_position(vehicle, dir_enum, distance)

        # Bounds check
        for r, c in new_vehicle.cells:
            if r < 0 or r >= self._board.size or c < 0 or c >= self._board.size:
                return MoveResult(
                    success=False,
                    message=f"Move would place vehicle '{vehicle_id}' out of bounds.",
                    move_count=self._move_count,
                    is_solved=self.is_solved(),
                )

        # Collision check: verify all swept cells are clear.
        # When a vehicle slides, every cell the leading edge passes through
        # must be unoccupied (no jumping over vehicles).
        swept = self._swept_cells(vehicle, dir_enum, distance)
        occupied: dict[tuple[int, int], str] = {}
        for other in self._board.vehicles:
            if other.id == vehicle_id:
                continue
            for cell in other.cells:
                occupied[cell] = other.id
        for cell in swept:
            if cell in occupied:
                return MoveResult(
                    success=False,
                    message=f"Vehicle '{vehicle_id}' is blocked by vehicle '{occupied[cell]}'.",
                    move_count=self._move_count,
                    is_solved=self.is_solved(),
                )

        # Apply move
        new_vehicles = tuple(
            new_vehicle if v.id == vehicle_id else v for v in self._board.vehicles
        )
        self._board = BoardState(vehicles=new_vehicles, size=self._board.size)
        self._move_count += 1

        solved = self.is_solved()
        if solved:
            msg = f"Moved '{vehicle_id}' {dir_enum.value} by {distance}. Puzzle solved in {self._move_count} moves!"
        else:
            msg = f"Moved '{vehicle_id}' {dir_enum.value} by {distance}."

        return MoveResult(
            success=True,
            message=msg,
            move_count=self._move_count,
            is_solved=solved,
        )

    def is_solved(self) -> bool:
        """Check if the target car has reached the exit."""
        target = self._board.vehicle_by_id(self.TARGET_ID)
        if target is None:
            return False
        # Target is horizontal, length 2, must reach col 4-5 (rightmost)
        return target.row == self.EXIT_ROW and target.col + target.length - 1 == self.EXIT_COL

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _direction_valid_for_vehicle(vehicle: Vehicle, direction: Direction) -> bool:
        if vehicle.orientation == Orientation.HORIZONTAL:
            return direction in (Direction.LEFT, Direction.RIGHT)
        return direction in (Direction.UP, Direction.DOWN)

    @staticmethod
    def _valid_directions(vehicle: Vehicle) -> tuple[Direction, Direction]:
        if vehicle.orientation == Orientation.HORIZONTAL:
            return (Direction.LEFT, Direction.RIGHT)
        return (Direction.UP, Direction.DOWN)

    @staticmethod
    def _swept_cells(
        vehicle: Vehicle, direction: Direction, distance: int
    ) -> list[tuple[int, int]]:
        """Return all cells the vehicle's leading edge sweeps through.

        These are the cells between the original edge and the destination edge
        (exclusive of original position, inclusive of destination).
        """
        cells: list[tuple[int, int]] = []
        if direction == Direction.RIGHT:
            for d in range(1, distance + 1):
                cells.append((vehicle.row, vehicle.col + vehicle.length - 1 + d))
        elif direction == Direction.LEFT:
            for d in range(1, distance + 1):
                cells.append((vehicle.row, vehicle.col - d))
        elif direction == Direction.DOWN:
            for d in range(1, distance + 1):
                cells.append((vehicle.row + vehicle.length - 1 + d, vehicle.col))
        elif direction == Direction.UP:
            for d in range(1, distance + 1):
                cells.append((vehicle.row - d, vehicle.col))
        return cells

    @staticmethod
    def _compute_new_position(
        vehicle: Vehicle, direction: Direction, distance: int
    ) -> Vehicle:
        row, col = vehicle.row, vehicle.col
        if direction == Direction.UP:
            row -= distance
        elif direction == Direction.DOWN:
            row += distance
        elif direction == Direction.LEFT:
            col -= distance
        elif direction == Direction.RIGHT:
            col += distance
        return Vehicle(
            id=vehicle.id,
            row=row,
            col=col,
            length=vehicle.length,
            orientation=vehicle.orientation,
        )
