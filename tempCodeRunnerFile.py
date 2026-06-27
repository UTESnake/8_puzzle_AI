# algorithms_uninformed.py
from collections import deque
import heapq
from utils import Node, extract_path

def _state_key(state):
    return tuple(tuple(row) for row in state)

def bfs(puzzle):
    start_node = Node(puzzle.state)
    if puzzle.is_goal(start_node.state): return []
    
    frontier = deque([start_node])
    frontier_states = {_state_key(start_node.state)}
    reached = set()

    while frontier:
        node = frontier.popleft()
        frontier_states.remove(_state_key(node.state))
        reached.add(_state_key(node.state))

        for next_state, action in puzzle.get_neighbors(node.state):
            key = _state_key(next_state)
            if key in reached or key in frontier_states:
                continue

            child = Node(next_state, node, action, node.g + 1)
            if puzzle.is_goal(next_state):
                return extract_path(child)
            frontier.append(child)
            frontier_states.add(key)
    return None

def dfs(puzzle):
    start_node = Node(puzzle.state)
    if puzzle.is_goal(start_node.state): return []
    
    frontier = [start_node]
    frontier_states = {_state_key(start_node.state)}
    reached = set()

    while frontier:
        node = frontier.pop()
        frontier_states.remove(_state_key(node.state))
        key = _state_key(node.state)
        if key in reached:
            continue
        reached.add(key)

        if puzzle.is_goal(node.state):
            return extract_path(node)

        for next_state, action in puzzle.get_neighbors(node.state):
            child_key = _state_key(next_state)
            if child_key not in reached and child_key not in frontier_states:
                frontier.append(Node(next_state, node, action, node.g + 1))
                frontier_states.add(child_key)
    return None

def ucs(puzzle):
    start_node = Node(puzzle.state)
    if puzzle.is_goal(start_node.state): return []

    frontier = []
    counter = 0
    heapq.heappush(frontier, (start_node.g, counter, start_node))
    reached_cost = {_state_key(start_node.state): start_node.g}

    while frontier:
        cost, _, node = heapq.heappop(frontier)
        if cost > reached_cost[_state_key(node.state)]:
            continue

        if puzzle.is_goal(node.state):
            return extract_path(node)
        
        for next_state, action in puzzle.get_neighbors(node.state):
            new_cost = cost + 1
            key = _state_key(next_state)
            if key not in reached_cost or new_cost < reached_cost[key]:
                reached_cost[key] = new_cost
                counter += 1
                child = Node(next_state, node, action, new_cost)
                heapq.heappush(frontier, (new_cost, counter, child))
    return None

def _is_cycle(node, state):
    key = _state_key(state)
    current = node
    while current is not None:
        if _state_key(current.state) == key:
            return True
        current = current.parent
    return False

def depth_limited_search(puzzle, limit):
    start_node = Node(puzzle.state)
    if puzzle.is_goal(start_node.state):
        return []

    cutoff_occurred = False
    frontier = [start_node]

    while frontier:
        node = frontier.pop()
        if puzzle.is_goal(node.state):
            return extract_path(node)

        if node.g >= limit:
            cutoff_occurred = True
            continue

        children = []
        for next_state, action in puzzle.get_neighbors(node.state):
            if not _is_cycle(node, next_state):
                children.append(Node(next_state, node, action, node.g + 1))

        # Đẩy ngược để khi pop vẫn duyệt theo thứ tự ACTIONS ban đầu.
        frontier.extend(reversed(children))

    return "cutoff" if cutoff_occurred else None

def iterative_deepening_search(puzzle, max_depth=60):
    for depth in range(max_depth + 1):
        result = depth_limited_search(puzzle, depth)
        if result != "cutoff":
            return result
    return None
