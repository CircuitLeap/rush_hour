"""Board rendering: ASCII and JSON representations."""

from __future__ import annotations

from rush_hour.models import BoardState


def _build_grid(board: BoardState) -> list[list[str]]:
    """Build a 2D grid from the board state. Empty cells are '.'."""
    grid = [["." for _ in range(board.size)] for _ in range(board.size)]
    for vehicle in board.vehicles:
        for r, c in vehicle.cells:
            grid[r][c] = vehicle.id
    return grid


def render_ascii(board: BoardState, move_count: int) -> str:
    """Render the board as an ASCII grid with coordinates and exit marker.

    Example output::

          0 1 2 3 4 5
        0 . . B . . .
        1 . . B C C C
        2 . X X . . .  -->
        3 . . . D . .
        4 . . . D . .
        5 . . . . . .

        Moves: 0
    """
    grid = _build_grid(board)
    lines: list[str] = []

    # Column header
    header = "    " + " ".join(str(c) for c in range(board.size))
    lines.append(header)

    for r in range(board.size):
        row_str = " ".join(grid[r][c] for c in range(board.size))
        prefix = f"  {r} "
        if r == 2:
            lines.append(f"{prefix}{row_str}  -->")
        else:
            lines.append(f"{prefix}{row_str}")

    lines.append("")
    lines.append(f"  Moves: {move_count}")
    return "\n".join(lines)


def render_json(board: BoardState, move_count: int, is_solved: bool) -> dict:
    """Return a structured dict representation of the board.

    Returns:
        {
            "board": [[str, ...], ...],  # 6x6 grid
            "vehicles": {
                "X": {"row": 2, "col": 0, "length": 2, "orientation": "horizontal"},
                ...
            },
            "move_count": int,
            "is_solved": bool,
        }
    """
    grid = _build_grid(board)
    vehicles = {}
    for v in board.vehicles:
        vehicles[v.id] = {
            "row": v.row,
            "col": v.col,
            "length": v.length,
            "orientation": v.orientation.value,
        }
    return {
        "board": grid,
        "vehicles": vehicles,
        "move_count": move_count,
        "is_solved": is_solved,
    }
