# algorithms_local.py -- Local-search algorithms for 8-puzzle
import math
import random
from utils import Node, extract_path, h_cost

MAX_LOCAL_STEPS = 500
MIN_RANDOM_RESTARTS = 10

def _state_key(state):
    return tuple(tuple(row) for row in state)

def _best_neighbor(puzzle, node):
    best = None
    best_h = float("inf")
    for next_state, action in puzzle.get_neighbors(node.state):
        h = h_cost(next_state, puzzle.goal)
        if h < best_h:
            best_h = h
            best = Node(next_state, node, action, node.depth + 1)
    return best, best_h

def _random_walk_node(puzzle, steps):
    node = Node(puzzle.state)
    previous_key = None

    for _ in range(steps):
        choices = []
        for next_state, action in puzzle.get_neighbors(node.state):
            key = _state_key(next_state)
            if key != previous_key:
                choices.append((next_state, action))
        if not choices:
            break

        next_state, action = random.choice(choices)
        previous_key = _state_key(node.state)
        node = Node(next_state, node, action, node.depth + 1)

    return node

def hill_climbing_simple(puzzle):
    current = Node(puzzle.state)

    for _ in range(MAX_LOCAL_STEPS):
        if puzzle.is_goal(current.state):
            return extract_path(current)

        current_h = h_cost(current.state, puzzle.goal)
        moved = False

        for next_state, action in puzzle.get_neighbors(current.state):
            next_h = h_cost(next_state, puzzle.goal)
            # Value(n) = -h(n), so Value(next) > Value(current) means next_h < current_h.
            if next_h < current_h:
                current = Node(next_state, current, action, current.depth + 1)
                moved = True
                break

        if not moved:
            return extract_path(current)

    return extract_path(current)

def hill_climbing_steepest(puzzle):
    current = Node(puzzle.state)

    for _ in range(MAX_LOCAL_STEPS):
        if puzzle.is_goal(current.state):
            return extract_path(current)

        current_h = h_cost(current.state, puzzle.goal)
        best, best_h = _best_neighbor(puzzle, current)

        if best is None or best_h >= current_h:
            return extract_path(current)

        current = best

    return extract_path(current)

def hill_climbing_stochastic(puzzle):
    current = Node(puzzle.state)

    for _ in range(MAX_LOCAL_STEPS):
        if puzzle.is_goal(current.state):
            return extract_path(current)

        current_h = h_cost(current.state, puzzle.goal)
        better_neighbors = []

        for next_state, action in puzzle.get_neighbors(current.state):
            if h_cost(next_state, puzzle.goal) < current_h:
                better_neighbors.append(Node(next_state, current, action, current.depth + 1))

        if not better_neighbors:
            return extract_path(current)

        current = random.choice(better_neighbors)

    return extract_path(current)

def hill_climbing_random_restart(puzzle, max_i=10, random_walk_depth=20):
    max_i = max(max_i, MIN_RANDOM_RESTARTS)
    candidates = [Node(puzzle.state)]
    candidates.extend(_random_walk_node(puzzle, random_walk_depth) for _ in range(max_i))
    best_result = None

    for start in sorted(candidates, key=lambda node: h_cost(node.state, puzzle.goal)):
        current = start

        for _ in range(MAX_LOCAL_STEPS):
            if puzzle.is_goal(current.state):
                return extract_path(current)

            current_h = h_cost(current.state, puzzle.goal)
            best, best_h = _best_neighbor(puzzle, current)

            if best is None or best_h >= current_h:
                break

            current = best

        if best_result is None or h_cost(current.state, puzzle.goal) < h_cost(best_result.state, puzzle.goal):
            best_result = current

    return extract_path(best_result) if best_result else []

def local_beam_search(puzzle, k=4, random_walk_depth=12):
    beams = [Node(puzzle.state)]
    beams.extend(_random_walk_node(puzzle, random_walk_depth) for _ in range(k - 1))
    seen = {_state_key(node.state) for node in beams}
    best_seen = min(beams, key=lambda node: h_cost(node.state, puzzle.goal))

    for _ in range(MAX_LOCAL_STEPS):
        candidates = []

        for node in beams:
            if puzzle.is_goal(node.state):
                return extract_path(node)

            for next_state, action in puzzle.get_neighbors(node.state):
                key = _state_key(next_state)
                if key not in seen:
                    child = Node(next_state, node, action, node.depth + 1)
                    candidates.append(child)
                    seen.add(key)
                    if h_cost(child.state, puzzle.goal) < h_cost(best_seen.state, puzzle.goal):
                        best_seen = child

        if not candidates:
            return extract_path(best_seen)

        candidates.sort(key=lambda node: h_cost(node.state, puzzle.goal))
        beams = candidates[:k]

    return extract_path(best_seen)

def simulated_annealing(
    puzzle,
    initial_temperature=18.0,
    cooling_rate=0.985,
    min_temperature=0.05,
    max_steps=1500,
):
    """Tìm kiếm mô phỏng tôi luyện, cho phép đi tới trạng thái xấu hơn lúc đầu."""
    current = Node(puzzle.state)
    best = current
    temperature = initial_temperature
    previous_key = None

    for _ in range(max_steps):
        if puzzle.is_goal(current.state):
            return extract_path(current)
        if temperature < min_temperature:
            break

        neighbors = [
            (state, action)
            for state, action in puzzle.get_neighbors(current.state)
            if _state_key(state) != previous_key
        ]
        if not neighbors:
            break

        next_state, action = random.choice(neighbors)
        current_h = h_cost(current.state, puzzle.goal)
        next_h = h_cost(next_state, puzzle.goal)
        improvement = current_h - next_h

        if improvement > 0 or random.random() < math.exp(improvement / temperature):
            previous_key = _state_key(current.state)
            current = Node(next_state, current, action, current.depth + 1)
            if next_h < h_cost(best.state, puzzle.goal):
                best = current

        temperature *= cooling_rate

    return extract_path(best)
