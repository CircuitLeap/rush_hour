"""Automated evaluation of candidate Rush Hour solutions.

Usage:
    python solution_checker.py <candidate_module>

The candidate module must expose a function:

    def solve(game: RushHourGame) -> None

that interacts with the game by calling game.move() until game.is_solved().
"""

import importlib
import sys
import time

from rush_hour import RushHourGame, list_puzzles


def evaluate_solver(solve_fn, puzzle_name: str) -> dict:
    """Run a solver on a single puzzle and return results."""
    game = RushHourGame.from_puzzle(puzzle_name)

    start = time.time()
    error = None
    try:
        solve_fn(game)
    except Exception as e:
        error = str(e)
    elapsed = time.time() - start

    if error:
        return {
            "puzzle": puzzle_name,
            "status": "ERROR",
            "moves": None,
            "time": elapsed,
            "error": error,
        }

    state = game.get_state(format="json")
    if not state["is_solved"]:
        return {
            "puzzle": puzzle_name,
            "status": "UNSOLVED",
            "moves": state["move_count"],
            "time": elapsed,
            "error": None,
        }

    return {
        "puzzle": puzzle_name,
        "status": "SOLVED",
        "moves": state["move_count"],
        "time": round(elapsed, 2),
        "error": None,
    }


def run_evaluation(solve_fn, puzzle_names: list[str] | None = None):
    """Evaluate a solver across puzzles and print results."""
    if puzzle_names is None:
        puzzle_names = [p["name"] for p in list_puzzles()]

    print(f"Evaluating solver on {len(puzzle_names)} puzzles...\n")
    print(f"{'Puzzle':<20} {'Status':<10} {'Moves':>6} {'Time':>8}")
    print("-" * 50)

    results = []
    for name in puzzle_names:
        result = evaluate_solver(solve_fn, name)
        results.append(result)

        status = result["status"]
        moves = str(result["moves"]) if result["moves"] is not None else "-"
        elapsed = f"{result['time']:.1f}s" if result["time"] is not None else "-"

        print(f"{name:<20} {status:<10} {moves:>6} {elapsed:>8}")

        if result["error"]:
            print(f"  Error: {result['error']}")

    # Summary
    solved = [r for r in results if r["status"] == "SOLVED"]
    total = len(results)
    print(f"\n{'=' * 50}")
    print(f"Solved: {len(solved)}/{total}")

    if solved:
        total_time = sum(r["time"] for r in solved)
        print(f"Total solve time: {total_time:.1f}s")

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python solution_checker.py <candidate_module>")
        print()
        print("The candidate module must expose: def solve(game: RushHourGame) -> None")
        print()
        print("Example:")
        print("  python solution_checker.py my_solution")
        sys.exit(1)

    module_name = sys.argv[1]
    if module_name.endswith(".py"):
        module_name = module_name[:-3]

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        print(f"Error: Could not import module '{module_name}'.")
        sys.exit(1)

    if not hasattr(module, "solve"):
        print(f"Error: Module '{module_name}' must expose a 'solve(game)' function.")
        sys.exit(1)

    run_evaluation(module.solve)


if __name__ == "__main__":
    main()
