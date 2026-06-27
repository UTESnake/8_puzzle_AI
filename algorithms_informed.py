# algorithms_informed.py
import heapq
import time

from algorithm_core import (
    ACTION_ORDER,
    SearchNode,
    heuristic,
    neighbors,
    puzzle_states,
    result_from_node,
    solvable,
    summary,
    timed_out,
)
from utils import SearchResult


def greedy(puzzle, max_nodes=100000, max_time_ms=30000, action_order=ACTION_ORDER):
    start, goal = puzzle_states(puzzle)
    if start == goal:
        return SearchResult([])
    if not solvable(start, goal):
        return None

    start_time = time.perf_counter()
    h_start = heuristic(start, goal)
    frontier = []
    counter = 0
    heapq.heappush(frontier, (h_start, counter, SearchNode(start, h=h_start)))
    reached = {start}
    expanded = 0
    generated = 1
    max_frontier = 1

    while frontier:
        if expanded >= max_nodes or timed_out(start_time, max_time_ms):
            return None

        _, _, node = heapq.heappop(frontier)
        expanded += 1
        if node.state == goal:
            return result_from_node(
                node,
                summary(expanded, generated, max_frontier, len(reached)),
            )

        next_states = neighbors(node.state, action_order)
        generated += len(next_states)

        for action, next_state in next_states:
            if next_state in reached:
                continue

            reached.add(next_state)
            counter += 1
            h = heuristic(next_state, goal)
            heapq.heappush(
                frontier,
                (
                    h,
                    counter,
                    SearchNode(
                        state=next_state,
                        parent=node,
                        action=action,
                        g=node.g + 1,
                        depth=node.depth + 1,
                        h=h,
                    ),
                ),
            )

        max_frontier = max(max_frontier, len(frontier))

    return None


def a_star(puzzle, max_nodes=100000, max_time_ms=30000, action_order=ACTION_ORDER):
    start, goal = puzzle_states(puzzle)
    if start == goal:
        return SearchResult([])
    if not solvable(start, goal):
        return None

    start_time = time.perf_counter()
    h_start = heuristic(start, goal)
    start_node = SearchNode(start, h=h_start)
    frontier = []
    counter = 0
    heapq.heappush(frontier, (start_node.f, counter, start_node))
    best_g = {start: 0}
    expanded = 0
    generated = 1
    max_frontier = 1

    while frontier:
        if expanded >= max_nodes or timed_out(start_time, max_time_ms):
            return None

        _, _, node = heapq.heappop(frontier)
        if node.g > best_g.get(node.state, float("inf")):
            continue

        expanded += 1
        if node.state == goal:
            return result_from_node(
                node,
                summary(expanded, generated, max_frontier, len(best_g)),
            )

        next_states = neighbors(node.state, action_order)
        generated += len(next_states)

        for action, next_state in next_states:
            new_g = node.g + 1
            if new_g >= best_g.get(next_state, float("inf")):
                continue

            best_g[next_state] = new_g
            counter += 1
            h = heuristic(next_state, goal)
            child = SearchNode(
                state=next_state,
                parent=node,
                action=action,
                g=new_g,
                depth=node.depth + 1,
                h=h,
            )
            heapq.heappush(frontier, (child.f, counter, child))

        max_frontier = max(max_frontier, len(frontier))

    return None


def _ida_star_search(start, goal, threshold, max_nodes, stats, action_order):
    min_exceeded = float("inf")
    start_node = SearchNode(start, g=0, depth=0, h=heuristic(start, goal))
    stack = [(start_node, {start})]

    while stack:
        if stats["expanded"] >= max_nodes:
            return {"found": False, "node": None, "min_exceeded": float("inf")}

        node, path_set = stack.pop()
        if node.f > threshold:
            min_exceeded = min(min_exceeded, node.f)
            continue

        stats["expanded"] += 1
        stats["max_frontier"] = max(stats["max_frontier"], len(stack))
        if node.state == goal:
            return {"found": True, "node": node, "min_exceeded": min_exceeded}

        next_states = neighbors(node.state, action_order)
        stats["generated"] += len(next_states)
        for action, next_state in next_states:
            if next_state in path_set:
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
            child_path_set = set(path_set)
            child_path_set.add(next_state)
            stack.append((child, child_path_set))
            stats["max_frontier"] = max(stats["max_frontier"], len(stack))

    return {"found": False, "node": None, "min_exceeded": min_exceeded}


def ida_star(
    puzzle,
    max_iterations=100,
    max_nodes=100000,
    max_time_ms=30000,
    action_order=ACTION_ORDER,
):
    start, goal = puzzle_states(puzzle)
    if start == goal:
        return SearchResult([])
    if not solvable(start, goal):
        return None

    start_time = time.perf_counter()
    threshold = heuristic(start, goal)
    stats = {"expanded": 0, "generated": 1, "max_frontier": 1}

    for iteration in range(max_iterations):
        if stats["expanded"] >= max_nodes or timed_out(start_time, max_time_ms):
            return None

        result = _ida_star_search(start, goal, threshold, max_nodes, stats, action_order)
        if result["found"]:
            details = [
                f"found with threshold {threshold}.",
                f"{iteration + 1} iterations; expanded {stats['expanded']} nodes.",
            ]
            return result_from_node(result["node"], details)

        if result["min_exceeded"] == float("inf"):
            return None
        threshold = result["min_exceeded"]

    return None
