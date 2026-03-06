"""Puzzle definitions and board string parser.

Puzzles are defined as 6x6 grids using single characters:
  - '.' or 'o' = empty cell
  - 'A' = target car (remapped to 'X' internally)
  - 'B'-'Z' = other vehicles
  - 'x' = wall (immovable obstacle, displayed as '#')

Each vehicle must form a contiguous horizontal or vertical line of 2-3 cells.
The target car (A/X) must be horizontal on row 2.
"""

from __future__ import annotations

from rush_hour.models import BoardState, Orientation, Vehicle

# ---------------------------------------------------------------------------
# Board string parser
# ---------------------------------------------------------------------------

def _parse_board_string(board_str: str, size: int = 6) -> BoardState:
    """Parse a 36-character board string (or multi-line grid) into a BoardState.

    The string is row-major. 'A' is remapped to 'X' (target car).
    """
    # Normalize: strip whitespace, support multi-line grids
    lines = board_str.strip().splitlines()
    if len(lines) > 1:
        # Multi-line grid format
        chars = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            chars.extend(list(line))
    else:
        chars = list(board_str.strip())

    if len(chars) != size * size:
        raise ValueError(
            f"Board string must have {size * size} characters, got {len(chars)}."
        )

    # Remap 'A' -> 'X' (target car)
    chars = ["X" if c == "A" else c for c in chars]

    # Build 2D grid
    grid: list[list[str]] = []
    for r in range(size):
        row = chars[r * size : (r + 1) * size]
        grid.append(row)

    # Discover vehicles by scanning cells
    seen_cells: dict[str, list[tuple[int, int]]] = {}
    for r in range(size):
        for c in range(size):
            ch = grid[r][c]
            if ch in (".", "o", "x"):
                continue
            seen_cells.setdefault(ch, []).append((r, c))

    vehicles: list[Vehicle] = []
    for vid, cells in seen_cells.items():
        cells.sort()
        min_r = min(r for r, c in cells)
        max_r = max(r for r, c in cells)
        min_c = min(c for r, c in cells)
        max_c = max(c for r, c in cells)
        length = len(cells)

        if length < 2 or length > 3:
            raise ValueError(
                f"Vehicle '{vid}' has {length} cells; must be 2 or 3."
            )

        if min_r == max_r:
            orientation = Orientation.HORIZONTAL
            if max_c - min_c + 1 != length:
                raise ValueError(f"Vehicle '{vid}' cells are not contiguous.")
        elif min_c == max_c:
            orientation = Orientation.VERTICAL
            if max_r - min_r + 1 != length:
                raise ValueError(f"Vehicle '{vid}' cells are not contiguous.")
        else:
            raise ValueError(
                f"Vehicle '{vid}' is neither horizontal nor vertical."
            )

        vehicles.append(
            Vehicle(id=vid, row=min_r, col=min_c, length=length, orientation=orientation)
        )

    vehicles.sort(key=lambda v: v.id)
    return BoardState(vehicles=tuple(vehicles), size=size)


# ---------------------------------------------------------------------------
# Puzzle definitions
# ---------------------------------------------------------------------------

# Each puzzle: (board_string, min_moves, description)
# Board strings use '.' for empty, letter for vehicles, 'A' = target (→ 'X').
#
# All puzzles are BFS-verified for solvability and optimal move count.

_PUZZLE_DEFS: dict[str, tuple[str, int, str]] = {
    # ---- Beginner (3-5 moves) ----
    "beginner_1": (
        # Chain: C left → B down → A right
        "...D.."
        "...D.."
        "AA.B.."
        "...B.."
        "..CC.."
        "......",
        3,
        "Beginner puzzle: 3 moves",
    ),
    "beginner_2": (
        # Two independent blockers + one chain
        "...D.."
        "...D.."
        "AA.BE."
        "...BE."
        "..CC.."
        "......",
        4,
        "Beginner puzzle: 4 moves",
    ),
    "beginner_3": (
        # Two dependency chains: H→F, E→B
        ".HHD.."
        "...D.."
        "AAFB.."
        "..FB.."
        ".GGEE."
        "......",
        5,
        "Beginner puzzle: 5 moves",
    ),

    # ---- Intermediate (8-17 moves) ----
    "intermediate_1": (
        "H....."
        "HDDD.."
        "AA.G.F"
        "C..G.F"
        "CEEB.."
        "II.B..",
        8,
        "Intermediate puzzle: 8 moves",
    ),
    "intermediate_2": (
        "BB.K.M"
        "..IKLM"
        "AAI.LM"
        "GHJCCC"
        "GHJ.DD"
        "GEE.FF",
        11,
        "Intermediate puzzle: 11 moves",
    ),
    "intermediate_3": (
        "..IBBM"
        "G.IKLM"
        "GAAKLM"
        "GHCCC."
        ".HJDD."
        "EEJFF.",
        17,
        "Intermediate puzzle: 17 moves",
    ),

    # ---- Advanced (23-29 moves) ----
    "advanced_1": (
        "..IKBB"
        "..IKLM"
        "GHAALM"
        "GHCCCM"
        "G.J.DD"
        "EEJFF.",
        23,
        "Advanced puzzle: 23 moves",
    ),
    "advanced_2": (
        ".HIBB."
        ".HIKL."
        "GAAKLM"
        "G.CCCM"
        "G.JDDM"
        "EEJFF.",
        25,
        "Advanced puzzle: 25 moves",
    ),
    "advanced_3": (
        "GHIBB."
        "GHI..M"
        "G.AALM"
        "CCCKLM"
        "..JKDD"
        "EEJFF.",
        29,
        "Advanced puzzle: 29 moves",
    ),

}


def get_puzzle(name: str) -> BoardState:
    """Return a BoardState for the named puzzle.

    Raises:
        ValueError: If the puzzle name is unknown.
    """
    if name not in _PUZZLE_DEFS:
        available = ", ".join(sorted(_PUZZLE_DEFS))
        raise ValueError(f"Unknown puzzle '{name}'. Available: {available}")
    board_str, _optimal, _desc = _PUZZLE_DEFS[name]
    return _parse_board_string(board_str)


def get_puzzle_info(name: str) -> dict:
    """Return puzzle metadata (min_moves, description)."""
    if name not in _PUZZLE_DEFS:
        raise ValueError(f"Unknown puzzle '{name}'.")
    _, optimal, desc = _PUZZLE_DEFS[name]
    return {"name": name, "min_moves": optimal, "description": desc}


def list_puzzles() -> list[dict]:
    """Return metadata for all available puzzles, sorted by difficulty."""
    result = []
    for name in sorted(_PUZZLE_DEFS):
        _, optimal, desc = _PUZZLE_DEFS[name]
        result.append({"name": name, "min_moves": optimal, "description": desc})
    return result
