"""Shared 8-puzzle search helpers matching the reference zip semantics.

The reference algorithms use flat tuple states and actions that move the
blank tile (L/R/U/D).  The existing UI animates the numbered tile direction,
so successful paths are converted before returning to Pygame.
"""

from dataclasses import dataclass
import math
import time

from utils import SearchResult, flatten_state, is_solvable, manhattan_distance


ACTION_ORDER = "LRUD"
BLANK_MOVES = {
    "L": (0, -1),
    "R": (0, 1),
    "U": (-1, 0),
    "D": (1, 0),
}
UI_ACTION_FROM_BLANK = {
    "L": "right",
    "R": "left",
    "U": "down",
    "D": "up",
}


@dataclass
class SearchNode:
    state: tuple
    parent: object = None
    action: str = "Start"
    g: int = 0
    depth: int = 0
    h: int = 0

    @property
    def f(self):
        return self.g + self.h

    def __lt__(self, other):
        if self.f != other.f:
            return self.f < other.f
        return self.g < other.g


def puzzle_states(puzzle):
    return flatten_state(puzzle.state), flatten_state(puzzle.goal)


def state_size(state):
    size = int(math.sqrt(len(state)))
    return size if size * size == len(state) else 3


def neighbors(state, action_order=ACTION_ORDER):
    size = state_size(state)
    blank = state.index(0)
    row, col = divmod(blank, size)
    result = []

    for action in action_order:
        if action not in BLANK_MOVES:
            continue

        dr, dc = BLANK_MOVES[action]
        next_row, next_col = row + dr, col + dc
        if 0 <= next_row < size and 0 <= next_col < size:
            next_index = next_row * size + next_col
            new_state = list(state)
            new_state[blank], new_state[next_index] = new_state[next_index], new_state[blank]
            result.append((action, tuple(new_state)))

    return result


def heuristic(state, goal):
    return manhattan_distance(state, goal)


def solvable(start, goal):
    return is_solvable(start, goal)


def timed_out(start_time, max_time_ms):
    return (time.perf_counter() - start_time) * 1000 > max_time_ms


def blank_actions_from_node(node):
    actions = []
    current = node
    while current is not None and current.action != "Start":
        actions.append(current.action)
        current = current.parent
    return actions[::-1]


def to_ui_actions(blank_actions):
    return [UI_ACTION_FROM_BLANK[action] for action in blank_actions]


def result_from_blank_actions(blank_actions, details=None):
    return SearchResult(to_ui_actions(blank_actions), details)


def result_from_node(node, details=None):
    return result_from_blank_actions(blank_actions_from_node(node), details)


def summary(expanded, generated, max_frontier, reached):
    return [
        f"expanded {expanded} nodes; generated {generated} states.",
        f"max frontier {max_frontier}; reached {reached} states.",
    ]
