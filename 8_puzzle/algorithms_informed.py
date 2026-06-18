# algorithms_informed.py
import heapq
from utils import Node, extract_path, h_cost, f_cost

def _state_key(state):
    return tuple(tuple(row) for row in state)

def greedy(puzzle):
    start_node = Node(puzzle.state)
    if puzzle.is_goal(start_node.state): return []

    frontier = []
    counter = 0
    heapq.heappush(frontier, (h_cost(start_node.state, puzzle.goal), counter, start_node))
    reached = {_state_key(start_node.state)}

    while frontier:
        _, _, node = heapq.heappop(frontier)
        if puzzle.is_goal(node.state):
            return extract_path(node)
            
        for next_state, action in puzzle.get_neighbors(node.state):
            key = _state_key(next_state)
            if key not in reached:
                reached.add(key)
                counter += 1
                child = Node(next_state, node, action, node.depth + 1)
                h = h_cost(next_state, puzzle.goal)
                heapq.heappush(frontier, (h, counter, child))
    return None

def a_star(puzzle):
    start_node = Node(puzzle.state)
    if puzzle.is_goal(start_node.state): return []

    frontier = []
    counter = 0
    heapq.heappush(frontier, (f_cost(start_node, puzzle.goal), counter, start_node))
    reached = {_state_key(start_node.state)}

    while frontier:
        _, _, node = heapq.heappop(frontier)
        if puzzle.is_goal(node.state):
            return extract_path(node)

        for next_state, action in puzzle.get_neighbors(node.state):
            key = _state_key(next_state)
            if key not in reached:
                reached.add(key)
                counter += 1
                child = Node(next_state, node, action, node.depth + 1)
                heapq.heappush(frontier, (f_cost(child, puzzle.goal), counter, child))
    return None

def _ida_search(puzzle, node, threshold, path_keys, best_depth):
    # IDA* phải dùng chi phí đường đi thực tế: f(n) = depth + h(n).
    # Nếu dùng số ô sai vị trí làm g(n), f(n) không tăng theo độ sâu và
    # thuật toán có thể đệ quy cho tới khi vượt giới hạn của Python.
    value = node.depth + h_cost(node.state, puzzle.goal)
    if value > threshold:
        return None, value

    if puzzle.is_goal(node.state):
        return node, value

    next_threshold = float("inf")

    for next_state, action in puzzle.get_neighbors(node.state):
        key = _state_key(next_state)
        child_depth = node.depth + 1

        if key in path_keys:
            continue
        if best_depth.get(key, float("inf")) <= child_depth:
            continue

        best_depth[key] = child_depth
        path_keys.add(key)
        child = Node(next_state, node, action, child_depth)
        result, candidate_threshold = _ida_search(
            puzzle, child, threshold, path_keys, best_depth
        )
        path_keys.remove(key)

        if result is not None:
            return result, candidate_threshold
        next_threshold = min(next_threshold, candidate_threshold)

    return None, next_threshold

def ida_star(puzzle, max_threshold=80):
    start_node = Node(puzzle.state)
    start_key = _state_key(start_node.state)
    threshold = h_cost(start_node.state, puzzle.goal)

    while threshold <= max_threshold:
        result, next_threshold = _ida_search(
            puzzle,
            start_node,
            threshold,
            {start_key},
            {start_key: 0},
        )
        if result is not None:
            return extract_path(result)
        if next_threshold == float("inf"):
            return None
        threshold = next_threshold

    return None
