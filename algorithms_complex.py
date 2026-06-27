"""Search algorithms that model more complex 8-puzzle environments."""

from collections import deque
import heapq
import random
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


def _goal_positions(goal):
    positions = {}
    for row, values in enumerate(goal):
        for col, tile in enumerate(values):
            positions[tile] = (row, col)
    return positions


def _goal_adjacency(goal):
    """Tạo đồ thị ràng buộc vị trí giữa các ô kề nhau trong trạng thái đích."""
    size = len(goal)
    adjacency = {tile: set() for row in goal for tile in row}
    for row in range(size):
        for col in range(size):
            tile = goal[row][col]
            for dr, dc in ((1, 0), (0, 1)):
                nr, nc = row + dr, col + dc
                if nr < size and nc < size:
                    other = goal[nr][nc]
                    adjacency[tile].add(other)
                    adjacency[other].add(tile)
    return adjacency


def _revise(domains, left, right, goal_pos):
    """Loại giá trị của left không có hỗ trợ từ miền của right."""
    expected_dr = goal_pos[right][0] - goal_pos[left][0]
    expected_dc = goal_pos[right][1] - goal_pos[left][1]
    supported = set()

    for left_pos in domains[left]:
        for right_pos in domains[right]:
            actual_dr = right_pos[0] - left_pos[0]
            actual_dc = right_pos[1] - left_pos[1]
            if (actual_dr, actual_dc) == (expected_dr, expected_dc):
                supported.add(left_pos)
                break

    removed = len(domains[left]) - len(supported)
    if removed:
        domains[left] = supported
    return removed


def _ac3_domains(puzzle):
    """Lan truyền các ràng buộc vị trí đích và trả về miền đã nhất quán."""
    size = puzzle.size
    positions = [(row, col) for row in range(size) for col in range(size)]
    goal_pos = _goal_positions(puzzle.goal)
    adjacency = _goal_adjacency(puzzle.goal)
    domains = {tile: set(positions) for tile in goal_pos}

    # Neo ô trống tại vị trí đích. Các quan hệ hướng với ô kề sẽ lan truyền
    # vị trí duy nhất tới toàn bộ đồ thị 3x3.
    domains[0] = {goal_pos[0]}
    queue = deque(
        (left, right)
        for left, neighbors in adjacency.items()
        for right in neighbors
    )
    stats = {"arcs": 0, "removed": 0}

    while queue:
        left, right = queue.popleft()
        stats["arcs"] += 1
        removed = _revise(domains, left, right, goal_pos)
        if not removed:
            continue

        stats["removed"] += removed
        if not domains[left]:
            return None, stats

        for neighbor in adjacency[left]:
            if neighbor != right:
                queue.append((neighbor, left))

    return domains, stats


def _domain_distance(state, domains):
    """Khoảng cách nhỏ nhất từ mỗi ô tới một giá trị còn lại trong miền."""
    total = 0
    for row, values in enumerate(state):
        for col, tile in enumerate(values):
            if tile == 0:
                continue
            total += min(
                abs(row - target_row) + abs(col - target_col)
                for target_row, target_col in domains[tile]
            )
    return total


def ac3_search(puzzle, max_nodes=200000):
    """AC-3 tiền xử lý CSP, sau đó tìm đường đi hợp lệ bằng heuristic miền."""
    domains, ac3_stats = _ac3_domains(puzzle)
    if domains is None:
        return None

    start = Node(puzzle.state)
    frontier = [(_domain_distance(start.state, domains), 0, start)]
    best_depth = {_state_key(start.state): 0}
    counter = 0
    expanded = 0
    max_frontier = 1

    while frontier and expanded < max_nodes:
        _, _, node = heapq.heappop(frontier)
        key = _state_key(node.state)
        if node.depth != best_depth.get(key):
            continue

        expanded += 1
        if puzzle.is_goal(node.state):
            return SearchResult(extract_path(node), [
                "CSP: mỗi quân số là một biến, miền là các vị trí trên bảng.",
                (
                    f"AC-3 duyệt {ac3_stats['arcs']} cung, loại "
                    f"{ac3_stats['removed']} giá trị khỏi các miền."
                ),
                (
                    f"Tìm kiếm theo miền đã nhất quán: mở rộng {expanded} nút; "
                    f"frontier lớn nhất {max_frontier}."
                ),
            ])

        for next_state, action in puzzle.get_neighbors(node.state):
            depth = node.depth + 1
            next_key = _state_key(next_state)
            if depth >= best_depth.get(next_key, float("inf")):
                continue

            best_depth[next_key] = depth
            counter += 1
            child = Node(next_state, node, action, depth)
            priority = depth + _domain_distance(next_state, domains)
            heapq.heappush(frontier, (priority, counter, child))
        max_frontier = max(max_frontier, len(frontier))

    return None


def _conflict_count(state, goal):
    """Số vi phạm vị trí, dùng như hàm mục tiêu của Min-Conflicts."""
    misplaced = 0
    distance = 0
    goal_pos = _goal_positions(goal)

    for row, values in enumerate(state):
        for col, tile in enumerate(values):
            if tile == 0:
                continue
            target_row, target_col = goal_pos[tile]
            if (row, col) != (target_row, target_col):
                misplaced += 1
            distance += abs(row - target_row) + abs(col - target_col)

    return misplaced, distance


def min_conflicts_search(puzzle, max_nodes=200000):
    """Min-Conflicts thích nghi: chỉ sửa biến bằng phép trượt hợp lệ."""
    start = Node(puzzle.state)
    start_conflicts = _conflict_count(start.state, puzzle.goal)
    frontier = [
        (start_conflicts[0], start_conflicts[1], 0.0, 0, start)
    ]
    best_depth = {_state_key(start.state): 0}
    counter = 0
    expanded = 0
    max_frontier = 1

    while frontier and expanded < max_nodes:
        _, _, _, _, node = heapq.heappop(frontier)
        key = _state_key(node.state)
        if node.depth != best_depth.get(key):
            continue

        expanded += 1
        if puzzle.is_goal(node.state):
            return SearchResult(extract_path(node), [
                "Biến xung đột được sửa bằng cách đổi chỗ với ô trống.",
                "Chỉ giữ các phép gán tương ứng với một nước trượt hợp lệ.",
                (
                    f"Mở rộng {expanded} trạng thái; frontier lớn nhất "
                    f"{max_frontier}; dùng ngẫu nhiên để phá hòa."
                ),
            ])

        candidates = []
        for next_state, action in puzzle.get_neighbors(node.state):
            depth = node.depth + 1
            next_key = _state_key(next_state)
            if depth >= best_depth.get(next_key, float("inf")):
                continue
            conflicts = _conflict_count(next_state, puzzle.goal)
            candidates.append((conflicts, random.random(), next_state, action))

        # Min-Conflicts ưu tiên phép gán làm giảm số ràng buộc bị vi phạm.
        candidates.sort(key=lambda item: (item[0][0], item[0][1], item[1]))
        for conflicts, tie_breaker, next_state, action in candidates:
            depth = node.depth + 1
            next_key = _state_key(next_state)
            best_depth[next_key] = depth
            counter += 1
            child = Node(next_state, node, action, depth)
            heapq.heappush(
                frontier,
                (
                    conflicts[0],
                    conflicts[1],
                    tie_breaker,
                    counter,
                    child,
                ),
            )
        max_frontier = max(max_frontier, len(frontier))

    return None
