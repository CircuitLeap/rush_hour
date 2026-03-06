"""Demo script showing how to interact with the Rush Hour game API."""

from rush_hour import RushHourGame, list_puzzles


def main():
    print("=== Available Puzzles ===\n")
    for p in list_puzzles():
        print(f"  {p['name']:20s}  ({p['min_moves']} moves)")

    print("\n\n=== Playing beginner_1 ===\n")
    game = RushHourGame.from_puzzle("beginner_1")
    print(game.get_state(format="ascii"))

    # Solve it: C left 2, B down 2, X right 4
    moves = [
        ("C", "left", 2),
        ("B", "down", 2),
        ("X", "right", 4),
    ]

    for vid, direction, distance in moves:
        print(f"\n> move({vid!r}, {direction!r}, {distance})")
        result = game.move(vid, direction, distance)
        print(f"  {result.message}")
        if not result.is_solved:
            print(game.get_state(format="ascii"))

    print(f"\nSolved: {game.is_solved()}")
    print(f"Total moves: {game.get_state(format='json')['move_count']}")

    # Show what an invalid move looks like
    print("\n\n=== Error handling examples ===\n")
    game2 = RushHourGame.from_puzzle("beginner_1")

    bad_moves = [
        ("X", "up", 1),      # wrong direction for horizontal car
        ("Z", "right", 1),   # non-existent vehicle
        ("X", "right", 5),   # blocked by another vehicle
    ]

    for vid, direction, distance in bad_moves:
        result = game2.move(vid, direction, distance)
        print(f"move({vid!r}, {direction!r}, {distance}) -> {result.message}")

    # Show JSON format
    print("\n\n=== JSON output format ===\n")
    game3 = RushHourGame.from_puzzle("beginner_1")
    import json
    state = game3.get_state(format="json")
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
