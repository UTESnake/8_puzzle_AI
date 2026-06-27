# algorithms_local.py -- Local-search algorithms for 8-puzzle
import math
import random

from algorithm_core import (
    ACTION_ORDER,
    SearchNode,
    heuristic,
    neighbors,
    puzzle_states,
    result_from_node,
)

MAX_LOCAL_STEPS = 500
MIN_RANDOM_RESTARTS = 10


def _best_neighbor(node, goal, action_order=ACTION_ORDER):
    best = None
    best_h = float("inf")
    for action, next_state in neighbors(node.state, action_order):
        h = heuristic(next_state, goal)
        if h < best_h:
            best_h = h
            best = SearchNode(
                state=next_state,
                parent=node,
                action=action,
                g=node.g + 1,
                depth=node.depth + 1,
                h=h,
            )
    return best, best_h


def _random_walk_node(start, goal, steps):
    node = SearchNode(start, h=heuristic(start, goal))
    previous_state = None

    for _ in range(steps):
        choices = [
            (action, next_state)
            for action, next_state in neighbors(node.state)
            if next_state != previous_state
        ]
        if not choices:
            break

        action, next_state = random.choice(choices)
        previous_state = node.state
        node = SearchNode(
            state=next_state,
            parent=node,
            action=action,
            g=node.g + 1,
            depth=node.depth + 1,
            h=heuristic(next_state, goal),
        )

    return node


def hill_climbing_simple(puzzle):
    start, goal = puzzle_states(puzzle)
    current = SearchNode(start, h=heuristic(start, goal))

    for _ in range(MAX_LOCAL_STEPS):
        if current.state == goal:
            return result_from_node(current, ["goal reached."])

        current_h = heuristic(current.state, goal)
        moved = False

        for action, next_state in neighbors(current.state):
            next_h = heuristic(next_state, goal)
            if next_h < current_h:
                current = SearchNode(
                    state=next_state,
                    parent=current,
                    action=action,
                    g=current.g + 1,
                    depth=current.depth + 1,
                    h=next_h,
                )
                moved = True
                break

        if not moved:
            return result_from_node(current, [f"stuck at h={current_h}."])

    return result_from_node(current, [f"stopped after {MAX_LOCAL_STEPS} steps."])


def hill_climbing_steepest(puzzle):
    start, goal = puzzle_states(puzzle)
    current = SearchNode(start, h=heuristic(start, goal))

    for _ in range(MAX_LOCAL_STEPS):
        if current.state == goal:
            return result_from_node(current, ["goal reached."])

        current_h = heuristic(current.state, goal)
        best, best_h = _best_neighbor(current, goal)

        if best is None or best_h >= current_h:
            return result_from_node(current, [f"stuck at h={current_h}."])

        current = best

    return result_from_node(current, [f"stopped after {MAX_LOCAL_STEPS} steps."])


def hill_climbing_stochastic(puzzle):
    start, goal = puzzle_states(puzzle)
    current = SearchNode(start, h=heuristic(start, goal))

    for _ in range(MAX_LOCAL_STEPS):
        if current.state == goal:
            return result_from_node(current, ["goal reached."])

        current_h = heuristic(current.state, goal)
        better_neighbors = []

        for action, next_state in neighbors(current.state):
            next_h = heuristic(next_state, goal)
            if next_h < current_h:
                better_neighbors.append(
                    SearchNode(
                        state=next_state,
                        parent=current,
                        action=action,
                        g=current.g + 1,
                        depth=current.depth + 1,
                        h=next_h,
                    )
                )

        if not better_neighbors:
            return result_from_node(current, [f"stuck at h={current_h}."])

        current = random.choice(better_neighbors)

    return result_from_node(current, [f"stopped after {MAX_LOCAL_STEPS} steps."])


def hill_climbing_random_restart(puzzle, max_i=10, random_walk_depth=20):
    start, goal = puzzle_states(puzzle)
    max_i = max(max_i, MIN_RANDOM_RESTARTS)
    candidates = [SearchNode(start, h=heuristic(start, goal))]
    candidates.extend(_random_walk_node(start, goal, random_walk_depth) for _ in range(max_i))
    best_result = None

    for candidate in sorted(candidates, key=lambda node: heuristic(node.state, goal)):
        current = candidate

        for _ in range(MAX_LOCAL_STEPS):
            if current.state == goal:
                return result_from_node(current, ["goal reached after random restart."])

            current_h = heuristic(current.state, goal)
            best, best_h = _best_neighbor(current, goal)

            if best is None or best_h >= current_h:
                break

            current = best

        if best_result is None or heuristic(current.state, goal) < heuristic(best_result.state, goal):
            best_result = current

    if best_result is None:
        return result_from_node(SearchNode(start), ["no restart candidate."])
    return result_from_node(
        best_result,
        [f"best h={heuristic(best_result.state, goal)} after {max_i} restarts."],
    )


def local_beam_search(puzzle, k=4, random_walk_depth=12):
    start, goal = puzzle_states(puzzle)
    beams = [SearchNode(start, h=heuristic(start, goal))]
    beams.extend(_random_walk_node(start, goal, random_walk_depth) for _ in range(k - 1))
    seen = {node.state for node in beams}
    best_seen = min(beams, key=lambda node: heuristic(node.state, goal))

    for _ in range(MAX_LOCAL_STEPS):
        candidates = []

        for node in beams:
            if node.state == goal:
                return result_from_node(node, ["goal reached."])

            for action, next_state in neighbors(node.state):
                if next_state in seen:
                    continue

                h = heuristic(next_state, goal)
                child = SearchNode(
                    state=next_state,
                    parent=node,
                    action=action,
                    g=node.g + 1,
                    depth=node.depth + 1,
                    h=h,
                )
                candidates.append(child)
                seen.add(next_state)
                if h < heuristic(best_seen.state, goal):
                    best_seen = child

        if not candidates:
            return result_from_node(best_seen, [f"best h={heuristic(best_seen.state, goal)}."])

        candidates.sort(key=lambda node: heuristic(node.state, goal))
        beams = candidates[:k]

    return result_from_node(best_seen, [f"stopped after {MAX_LOCAL_STEPS} beam steps."])


def simulated_annealing(
    puzzle,
    initial_temperature=100.0,
    cooling_rate=0.995,
    min_temperature=0.01,
    max_steps=10000,
):
    start, goal = puzzle_states(puzzle)
    current = SearchNode(start, h=heuristic(start, goal))
    best = current
    temperature = initial_temperature

    for _ in range(max_steps):
        if current.state == goal:
            return result_from_node(current, ["goal reached."])
        if temperature < min_temperature:
            break

        options = neighbors(current.state)
        if not options:
            break

        action, next_state = random.choice(options)
        current_h = heuristic(current.state, goal)
        next_h = heuristic(next_state, goal)
        delta = next_h - current_h

        if delta < 0 or random.random() < math.exp(-delta / temperature):
            current = SearchNode(
                state=next_state,
                parent=current,
                action=action,
                g=current.g + 1,
                depth=current.depth + 1,
                h=next_h,
            )
            if next_h < heuristic(best.state, goal):
                best = current

        temperature *= cooling_rate

    return result_from_node(best, [f"best h={heuristic(best.state, goal)}."])
