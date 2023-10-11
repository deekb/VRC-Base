import gc
import math
from functools import lru_cache
import sys
import heapq


class Dijkstra:
    """
    Dijkstra's algorithm implementation to find the shortest path between two points on a 2D grid.

    Attributes:
        _start_position (tuple): The starting position as a tuple (x, y).
        _target_position (tuple): The goal position as a tuple (x, y).
        _valid_moves (list of tuples): A list of valid moves that an agent can make in the environment.
        _open_heap (list): A list to store nodes to be explored, ordered by cost.
        _closed_set (list): A list to store nodes that have been explored.
        _parent_dict (dict): A dictionary that maps child nodes to their parent nodes in the path.
        _g_values (dict): A dictionary that stores the cost from the start position to each node.
    """

    def __init__(self, start_pos, goal_pos, accessible_tiles, valid_moves):
        """
        Initialize the Dijkstra algorithm with start and goal points.
        :param start_pos: Tuple (x, y) representing the starting point.
        :param goal_pos: Tuple (x, y) representing the goal point.
        """
        self._start_position = start_pos
        self._target_position = goal_pos
        self._valid_moves = valid_moves
        self._move_costs = {
            move: math.sqrt(move[0] ** 2 + move[1] ** 2) for move in valid_moves
        }
        self._accessible_tiles = accessible_tiles  # Since sets are hashable,
        # we can improve lookup times by converting accessible_tiles to a set
        self._open_heap = []
        self._closed_set = set()
        self._parent_dict = {}
        self._g_values = {}

    def _insert_to_open_list(self, item):
        """
        Insert a node into the open_list while maintaining the sorted order based on the cost.

        :param item: Tuple (cost, position) to be inserted into the open_list.
        """
        heapq.heappush(self._open_heap, item)
        # self._open_heap.push(item)

    def _pop_lowest_cost_node(self):
        """
        Remove and return the node with the lowest cost from the open_list.

        :return: Tuple (cost, position) representing the node with the lowest cost.
        """
        return heapq.heappop(self._open_heap)
        # return self._open_heap.pop()

    def find_path(self):
        """
        Find the shortest path from the start position to the goal position using Dijkstra's algorithm.

        :return: Tuple containing the path as a list of positions and the list of visited positions.
        """
        self._parent_dict[self._start_position] = self._start_position
        self._g_values[self._start_position] = 0
        self._g_values[self._target_position] = float("inf")
        self._insert_to_open_list((0, self._start_position))

        # Sanity checks

        assert (
            self._start_position in self._accessible_tiles
        ), 'Tile "start_position" is not in accessible_tiles'
        assert (
            self._target_position in self._accessible_tiles
        ), 'Tile "target_position" is not in accessible_tiles'

        while self._open_heap:
            _, current_pos = self._pop_lowest_cost_node()
            self._closed_set.add(current_pos)

            if current_pos == self._target_position:
                break

            for neighbor_pos in self._get_valid_neighbors(current_pos):
                new_cost = self._g_values[current_pos] + self._calculate_cost(
                    current_pos, neighbor_pos
                )

                if neighbor_pos not in self._g_values:
                    self._g_values[neighbor_pos] = float("inf")

                if new_cost < self._g_values[neighbor_pos]:
                    self._g_values[neighbor_pos] = new_cost
                    self._parent_dict[neighbor_pos] = current_pos
                    self._insert_to_open_list((new_cost, neighbor_pos))

        gc.collect()

        print(f"Open heap: {sys.getsizeof(self._open_heap)}")
        print(f"Closed heap: {sys.getsizeof(self._closed_set.copy())}")
        print(f"G values: {sys.getsizeof(self._g_values.copy())}")
        print(f"Parent dict: {sys.getsizeof(self._parent_dict.copy())}")

        # print("Time taken: " + str(round((time.perf_counter() - start_time) * 1000)) + "ms")
        return self._extract_path(self._parent_dict), self._closed_set

    def _get_valid_neighbors(self, pos):
        """
        Get valid neighboring positions from the given position.

        :param pos: Tuple (x, y) representing the current position.
        :return: List of tuples representing the valid neighboring positions.
        """
        return {(pos[0] + move[0], pos[1] + move[1]) for move in self._valid_moves}

    @lru_cache(maxsize=0, typed=False)
    def _calculate_cost(self, start_pos, end_pos):
        """
        Calculate the cost from the start position to the end position.

        :param start_pos: Tuple (x, y) representing the start position.
        :param end_pos: Tuple (x, y) representing the end position.
        :return: Float value representing the cost from the start position to the end position.
        """
        if self._is_collision(start_pos, end_pos):
            return float("inf")

        return math.dist(start_pos, end_pos)
        # return math.sqrt(
        #     (end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2
        # )

    def _is_collision(self, start_pos, end_pos):
        """
        Check if there is a collision between the start and end positions with obstacles.

        :param start_pos: Tuple (x, y) representing the start position.
        :param end_pos: Tuple (x, y) representing the end position.
        :return: True if there is a collision, False otherwise.
        """
        return not (end_pos in self._accessible_tiles) or not (
            start_pos in self._accessible_tiles
        )

    def _extract_path(self, parent_dict):
        """
        Extract the path from the parent_dict starting from the goal position to the start position.

        :param parent_dict: Dictionary mapping child positions to their parent positions.
        :return: List of tuples representing the path from the start position to the goal position.
        """
        path = [self._target_position]
        current_pos = self._target_position

        while True:
            assert current_pos in parent_dict, "Heap exhausted: No Path to target"

            current_pos = parent_dict[current_pos]
            path.append(current_pos)

            if current_pos == self._start_position:
                break

        path.reverse()
        return path
