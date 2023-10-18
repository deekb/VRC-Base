import time
import os
import sys

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"
)

sys.path.append(src_dir)

from Dijkstra_HeapQ import Dijkstra

MAX_FPS = 60
DISPLAY_SCALING_FACTOR = 8
FIELD_SIZE = (122, 122)


def get_path(start_position, target_position):
    with open(os.path.join(os.pardir, os.pardir, "available_positions.txt"), "r") as f:
        accessible_tiles = set(eval(f.read()))

    valid_moves = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

    dijkstra = Dijkstra(start_position, target_position, accessible_tiles, valid_moves)

    start_time = time.perf_counter()

    try:
        path, visited_tiles = dijkstra.find_path()
    except AssertionError as e:
        print("Assertion Error:", e)
        path, visited_tiles = [], []

    print(
        f"[{__file__}]: Search took: {round((time.perf_counter() - start_time) * 1000)}ms"
    )

    return path, visited_tiles


def main():
    start_position = (6, 62)
    target_position = (115, 59)
    path, visited_tiles = get_path(start_position, target_position)


if __name__ == "__main__":
    main()
