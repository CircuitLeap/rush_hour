# Rush Hour Puzzle Solver — AI Agent Exercise

## Overview

Build a multi-agent system that solves [Rush Hour](https://en.wikipedia.org/wiki/Rush_Hour_(puzzle)) puzzles.

Rush Hour is a sliding puzzle played on a 6×6 grid. Vehicles (cars of length 2 or trucks of length 3) can only slide along their orientation axis (horizontal vehicles move left/right, vertical vehicles move up/down). The goal is to move the **target car (X)** to the right edge of the board (row 2, column 5).

## Game API

The game environment is a plain Python class — no framework dependencies. You decide how to wrap it (LangGraph tools, function calls, MCP, etc.).

```python
from rush_hour import RushHourGame, list_puzzles

# See all available puzzles
for p in list_puzzles():
    print(f"{p['name']}: {p['min_moves']} moves")

# Create a game
game = RushHourGame.from_puzzle("beginner_1")

# View the board
print(game.get_state(format="ascii"))   # visual grid
state = game.get_state(format="json")   # structured dict

# Make a move
result = game.move("X", "right", 2)
print(result.success)     # True/False
print(result.message)     # human-readable outcome
print(result.move_count)  # total moves so far
print(result.is_solved)   # puzzle complete?

# Check if solved
game.is_solved()  # True when X reaches the exit
```

### `get_state(format="ascii")`

Returns a string with the board grid, coordinates, and an exit marker:

```
     0 1 2 3 4 5
  0  . . . D . .
  1  . . . D . .
  2  X X . B . .  -->
  3  . . . B . .
  4  . . C C . .
  5  . . . . . .
```

### `get_state(format="json")`

Returns a dict:

```json
{
  "board": [[".", ".", ".", "D", ".", "."], ...],
  "vehicles": {
    "X": {"row": 2, "col": 0, "length": 2, "orientation": "horizontal"},
    "B": {"row": 2, "col": 3, "length": 2, "orientation": "vertical"},
    ...
  },
  "move_count": 0,
  "is_solved": false
}
```

### `move(vehicle_id, direction, distance)`

- **vehicle_id**: Single letter (`"X"`, `"B"`, `"C"`, etc.)
- **direction**: `"up"`, `"down"`, `"left"`, or `"right"`
- **distance**: Integer 1-5

Returns a `MoveResult` with `success`, `message`, `move_count`, and `is_solved`.

Invalid moves return `success=False` with a descriptive `message` — they do not raise exceptions and do not increment the move counter.

## Puzzles

9 puzzles across 3 difficulty levels:

| Difficulty   | Puzzles | Moves to Solve |
|-------------|---------|----------------|
| Beginner    | 3       | 3-5            |
| Intermediate| 3       | 8-17           |
| Advanced    | 3       | 23-29          |

Additional hidden puzzles may be used during evaluation.

## Your Task

Build a system that solves these puzzles. Your solution must expose:

```python
def solve(game: RushHourGame) -> None:
    """Solve the given Rush Hour puzzle by calling game.move() until game.is_solved()."""
    ...
```

### Evaluation

```bash
python solution_checker.py your_solution
```

The checker runs your solver on all puzzles and reports:

- **Status**: SOLVED / UNSOLVED / ERROR / TIMEOUT
- **Moves used**
- **Time** taken per puzzle

### What We're Looking For

- A working solution that solves puzzles across difficulty levels
- Thoughtful system design — how you decompose the problem, what agents/tools you create
- Clean, readable code
- Your reasoning about trade-offs (speed vs optimality, complexity vs simplicity)

There is no single correct architecture. Show us how you think.
