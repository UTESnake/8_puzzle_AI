# algorithms_uninformed.py
from collections import deque
import heapq
import time

from algorithm_core import (
    ACTION_ORDER,
    SearchNode,
    neighbors,
    puzzle_states,
    result_from_node,
    solvable,
    summary,
    timed_out,
)
from utils import SearchResult


def bfs(puzzle, max_nodes=100000, max_time_ms=30000, action_order=ACTION_ORDER):
    start, goal = puzzle_states(puzzle)
    if start == goal:
        return SearchResult([])
    if not solvable(start, goal):
        return None

    start_time = time.perf_counter()
    frontier = deque([SearchNode(start)])
    reached = {start}
    expanded = 0
    generated = 1
    max_frontier = 1

    while frontier:
        if expanded >= max_nodes or timed_out(start_time, max_time_ms):
            return None

        node = frontier.popleft()
        expanded += 1
        next_states = neighbors(node.state, action_order)
        generated += len(next_states)

        for action, next_state in next_states:
            if next_state in reached:
                continue

            reached.add(next_state)
            child = SearchNode(
                state=next_state,
                parent=node,
                action=action,
                g=node.g + 1,
                depth=node.depth + 1,
            )
            if next_state == goal:
                return result_from_node(
                    child,
                    summary(expanded, generated, max_frontier, len(reached)),
                )
            frontier.append(child)

        max_frontier = max(max_frontier, len(frontier))

    return None


def dfs(
    puzzle,
    max_depth=50,
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
    frontier = [SearchNode(start)]
    reached = {start: 0}
    expanded = 0
    generated = 1
    max_frontier = 1

    while frontier:
        if expanded >= max_nodes or timed_out(start_time, max_time_ms):
            return None

        node = frontier.pop()
        if node.depth > max_depth:
            continue

        expanded += 1
        if node.state == goal:
            return result_from_node(
                node,
                summary(expanded, generated, max_frontier, len(reached)),
            )

        next_states = neighbors(node.state, action_order)
        generated += len(next_states)

        for action, next_state in next_states:
            child_depth = node.depth + 1
            if next_state not in reached or child_depth < reached[next_state]:
                reached[next_state] = child_depth
                frontier.append(
                    SearchNode(
                        state=next_state,
                        parent=node,
                        action=action,
                        g=node.g + 1,
                        depth=child_depth,
                    )
                )

        max_frontier = max(max_frontier, len(frontier))

    return None


def ucs(puzzle, max_nodes=100000, max_time_ms=30000, action_order=ACTION_ORDER):
    start, goal = puzzle_states(puzzle)
    if start == goal:
        return SearchResult([])
    if not solvable(start, goal):
        return None

    start_time = time.perf_counter()
    frontier = []
    counter = 0
    heapq.heappush(frontier, (0, counter, SearchNode(start)))
    best_g = {start: 0}
    expanded = 0
    generated = 1
    max_frontier = 1

    while frontier:
        if expanded >= max_nodes or timed_out(start_time, max_time_ms):
            return None

        cost, _, node = heapq.heappop(frontier)
        if cost > best_g.get(node.state, float("inf")):
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
            heapq.heappush(
                frontier,
                (
                    new_g,
                    counter,
                    SearchNode(
                        state=next_state,
                        parent=node,
                        action=action,
                        g=new_g,
                        depth=node.depth + 1,
                    ),
                ),
            )

        max_frontier = max(max_frontier, len(frontier))

    return None


def _depth_limited_search(start, goal, limit, action_order, stats):
    frontier = [(SearchNode(start), {start})]

    while frontier:
        node, path_set = frontier.pop()
        stats["expanded"] += 1
        stats["reached"].add(node.state)
        stats["max_frontier"] = max(stats["max_frontier"], len(frontier))

        if node.state == goal:
            return node

        if node.depth >= limit:
            continue

        next_states = neighbors(node.state, action_order)
        stats["generated"] += len(next_states)
        for action, next_state in next_states:
            if next_state in path_set:
                continue

            child = SearchNode(
                state=next_state,
                parent=node,
                action=action,
                g=node.g + 1,
                depth=node.depth + 1,
            )
            child_path_set = set(path_set)
            child_path_set.add(next_state)
            stats["reached"].add(next_state)
            frontier.append((child, child_path_set))
            stats["max_frontier"] = max(stats["max_frontier"], len(frontier))

    return None


def depth_limited_search(puzzle, limit):
    start, goal = puzzle_states(puzzle)
    if start == goal:
        return SearchResult([])

    stats = {"expanded": 0, "generated": 1, "max_frontier": 1, "reached": {start}}
    result = _depth_limited_search(start, goal, limit, ACTION_ORDER, stats)
    if result is None:
        return None
    return result_from_node(result, [f"found at depth limit {limit}."])


def iterative_deepening_search(
    puzzle,
    max_depth=30,
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
    stats = {"expanded": 0, "generated": 1, "max_frontier": 1, "reached": {start}}

    for depth in range(max_depth + 1):
        if stats["expanded"] >= max_nodes or timed_out(start_time, max_time_ms):
            return None

        result = _depth_limited_search(start, goal, depth, action_order, stats)
        if result is not None:
            details = [f"found at depth limit {depth}."]
            details.extend(
                summary(
                    stats["expanded"],
                    stats["generated"],
                    stats["max_frontier"],
                    len(stats["reached"]),
                )
            )
            return result_from_node(result, details)

    return None
