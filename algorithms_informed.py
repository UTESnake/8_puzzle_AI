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

def _ida_search(puzzle, node, threshold):
    value = f_cost(node, puzzle.goal)
    if value > threshold:
        return None, value

    if puzzle.is_goal(node.state):
        return node, value

    next_threshold = float("inf")
    current = node

    for next_state, action in puzzle.get_neighbors(node.state):
        key = _state_key(next_state)
        is_cycle = False
        while current is not None:
            if _state_key(current.state) == key:
                is_cycle = True
                break
            current = current.parent

        current = node
        if is_cycle:
            continue

        child = Node(next_state, node, action, node.depth + 1)
        result, candidate_threshold = _ida_search(puzzle, child, threshold)
        if result is not None:
            return result, candidate_threshold
        next_threshold = min(next_threshold, candidate_threshold)

    return None, next_threshold

def ida_star(puzzle, max_threshold=80):
    start_node = Node(puzzle.state)
    threshold = f_cost(start_node, puzzle.goal)

    while threshold <= max_threshold:
        result, next_threshold = _ida_search(puzzle, start_node, threshold)
        if result is not None:
            return extract_path(result)
        if next_threshold == float("inf"):
            return None
        threshold = next_threshold

    return None
