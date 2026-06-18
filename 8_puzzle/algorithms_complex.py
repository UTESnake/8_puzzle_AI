"""Search algorithms that model more complex 8-puzzle environments."""

import heapq
from utils import Node, extract_path, h_cost


class SearchResult(list):
    """Danh sách bước đi kèm thông tin để UI minh họa cách tìm kiếm."""

    def __init__(self, path, details):
        super().__init__(path)
        self.details = details


INVERSE_ACTION = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left",
}
VISIBLE_TILES = {1, 2, 3, 4}
PARTIAL_ACTION_ORDER = {"up": 0, "down": 1, "left": 2, "right": 3}
BACKTRACK_ACTION_ORDER = {"down": 0, "up": 1, "left": 2, "right": 3}


def _state_key(state):
    return tuple(tuple(row) for row in state)


def search_without_start_state(puzzle):
    """Tìm từ goal về trạng thái hiện tại, không mở frontier tại start."""
    target = puzzle.state
    root = Node(puzzle.goal)
    frontier = [(h_cost(root.state, target), 0, root)]
    best_depth = {_state_key(root.state): 0}
    counter = 0
    expanded = 0
    max_frontier = 1

    while frontier:
        _, _, node = heapq.heappop(frontier)
        expanded += 1
        if node.state == target:
            reverse_path = extract_path(node)
            path = [INVERSE_ACTION[action] for action in reversed(reverse_path)]
            return SearchResult(path, [
                "Mô hình: tìm ngược từ Goal → trạng thái hiện tại.",
                f"Đã mở rộng {expanded} nút; frontier lớn nhất {max_frontier}.",
            ])

        for next_state, action in puzzle.get_neighbors(node.state):
            depth = node.depth + 1
            key = _state_key(next_state)
            if depth >= best_depth.get(key, float("inf")):
                continue

            best_depth[key] = depth
            counter += 1
            child = Node(next_state, node, action, depth)
            priority = depth + h_cost(next_state, target)
            heapq.heappush(frontier, (priority, counter, child))
        max_frontier = max(max_frontier, len(frontier))

    return None


def _partial_observation_h(state, goal):
    """Heuristic chỉ quan sát các quân 1-4; các quân còn lại đang bị che."""
    goal_pos = {}
    for r, row in enumerate(goal):
        for c, value in enumerate(row):
            if value in VISIBLE_TILES:
                goal_pos[value] = (r, c)

    distance = 0
    for r, row in enumerate(state):
        for c, value in enumerate(row):
            if value in goal_pos:
                gr, gc = goal_pos[value]
                distance += abs(r - gr) + abs(c - gc)
    return distance


def partially_observable_search(puzzle, max_nodes=200000):
    """Greedy best-first trên phần quan sát được của trạng thái."""
    start = Node(puzzle.state)
    frontier = [(_partial_observation_h(start.state, puzzle.goal), 0, 0, start)]
    best_depth = {_state_key(start.state): 0}
    counter = 0
    expanded = 0
    max_frontier = 1

    while frontier and expanded < max_nodes:
        _, _, _, node = heapq.heappop(frontier)
        expanded += 1
        if puzzle.is_goal(node.state):
            return SearchResult(extract_path(node), [
                "Quan sát: chỉ thấy vị trí các ô 1, 2, 3, 4.",
                "Chọn nhánh Greedy chỉ theo phần đang nhìn thấy.",
                f"Đã mở rộng {expanded} nút; frontier lớn nhất {max_frontier}.",
            ])

        for next_state, action in puzzle.get_neighbors(node.state):
            depth = node.depth + 1
            key = _state_key(next_state)
            if depth >= best_depth.get(key, float("inf")):
                continue

            best_depth[key] = depth
            counter += 1
            child = Node(next_state, node, action, depth)
            priority = _partial_observation_h(next_state, puzzle.goal)
            heapq.heappush(
                frontier,
                (priority, PARTIAL_ACTION_ORDER[action], counter, child),
            )
        max_frontier = max(max_frontier, len(frontier))

    return None


def _and_or_search(puzzle, node, threshold, path_keys, stats):
    stats["expanded"] += 1
    value = node.depth + h_cost(node.state, puzzle.goal)
    if value > threshold:
        return None, value
    if puzzle.is_goal(node.state):
        return node, value

    next_threshold = float("inf")
    actions = sorted(
        puzzle.get_neighbors(node.state),
        key=lambda item: h_cost(item[0], puzzle.goal),
    )

    # OR: chọn một hành động. AND: mọi kết quả của hành động phải giải được.
    # 8-puzzle là xác định nên mỗi hành động hiện có đúng một kết quả.
    for next_state, action in actions:
        key = _state_key(next_state)
        if key in path_keys:
            continue

        path_keys.add(key)
        child = Node(next_state, node, action, node.depth + 1)
        result, candidate = _and_or_search(
            puzzle, child, threshold, path_keys, stats
        )
        path_keys.remove(key)

        if result is not None:
            return result, candidate
        next_threshold = min(next_threshold, candidate)

    return None, next_threshold


def and_or_search(puzzle, max_depth=80):
    start = Node(puzzle.state)
    start_key = _state_key(start.state)
    threshold = h_cost(start.state, puzzle.goal)
    stats = {"expanded": 0, "iterations": 0}

    while threshold <= max_depth:
        stats["iterations"] += 1
        result, next_threshold = _and_or_search(
            puzzle, start, threshold, {start_key}, stats
        )
        if result is not None:
            return SearchResult(extract_path(result), [
                "Cây kế hoạch: OR chọn hành động, AND kiểm tra mọi kết quả.",
                f"{stats['iterations']} vòng ngưỡng; mở rộng {stats['expanded']} nút.",
                "8-puzzle xác định: mỗi hành động chỉ có 1 kết quả.",
            ])
        if next_threshold == float("inf"):
            return None
        threshold = next_threshold

    return None


def _backtrack(puzzle, node, limit, path_keys, stats):
    stats["expanded"] += 1
    if puzzle.is_goal(node.state):
        return node
    if node.depth + h_cost(node.state, puzzle.goal) > limit:
        stats["pruned"] += 1
        return None

    neighbors = sorted(
        puzzle.get_neighbors(node.state),
        key=lambda item: (
            h_cost(item[0], puzzle.goal),
            BACKTRACK_ACTION_ORDER[item[1]],
        ),
    )
    for next_state, action in neighbors:
        key = _state_key(next_state)
        if key in path_keys:
            continue

        path_keys.add(key)
        child = Node(next_state, node, action, node.depth + 1)
        result = _backtrack(puzzle, child, limit, path_keys, stats)
        path_keys.remove(key)
        if result is not None:
            return result
        stats["backtracks"] += 1

    return None


def backtracking_search(puzzle, max_depth=80):
    """Quay lui theo độ sâu, cắt nhánh bằng khoảng cách Manhattan."""
    start = Node(puzzle.state)
    start_key = _state_key(start.state)
    first_limit = h_cost(start.state, puzzle.goal)
    # Cho phép chọn một nhánh không tối ưu ngay từ đầu để minh họa rõ
    # hành vi quay lui, thay vì trùng đường đi tối ưu của AND-OR.
    initial_limit = min(max_depth, first_limit + 10)
    stats = {
        "expanded": 0,
        "backtracks": 0,
        "pruned": 0,
        "limits": 0,
    }

    for limit in range(initial_limit, max_depth + 1):
        stats["limits"] += 1
        result = _backtrack(puzzle, start, limit, {start_key}, stats)
        if result is not None:
            return SearchResult(extract_path(result), [
                f"Quay lui DFS với giới hạn cuối là {limit}.",
                "Ưu tiên nhánh riêng để không trùng lời giải tối ưu.",
                f"Mở rộng {stats['expanded']} nút; quay lui {stats['backtracks']} lần.",
                f"Cắt {stats['pruned']} nhánh không thể đạt đích trong giới hạn.",
            ])

    return None
