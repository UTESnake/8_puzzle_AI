# utils.py

# Hướng di chuyển của ô trống (Delta Row, Delta Column)
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
# Puzzle.move() nhận hướng của quân số/người chơi, ngược với hướng ô trống.
DIR_MAP = {(-1, 0): "down", (1, 0): "up", (0, -1): "right", (0, 1): "left"}

class Node:
    def __init__(self, state, parent=None, action=None, depth=0):
        self.state = state
        self.parent = parent
        self.action = action  # Hành động để đạt trạng thái này ("up", "down",...)
        self.depth = depth    # Độ sâu dùng cho BFS/DFS/IDS, không phải g(n)
        self.g = depth        # Giữ tương thích với code cũ; g(n) đánh giá dùng g_cost().

    def __lt__(self, other):
        return self.depth < other.depth

def extract_path(node):
    """Truy vết các thao tác từ đích về trạng thái ban đầu."""
    path = []
    curr = node
    while curr.parent is not None:
        path.append(curr.action)
        curr = curr.parent
    return path[::-1]

def manhattan_distance(state, goal):
    """h(n): tổng khoảng cách Manhattan từ state đến goal."""
    goal_pos = {}
    for gr in range(3):
        for gc in range(3):
            goal_pos[goal[gr][gc]] = (gr, gc)

    dist = 0
    for r in range(3):
        for c in range(3):
            val = state[r][c]
            if val != 0:
                gr, gc = goal_pos[val]
                dist += abs(r - gr) + abs(c - gc)
    return dist

def misplaced_tiles(state, goal):
    """Đếm số ô số sai vị trí, không tính ô trống."""
    count = 0
    for r in range(3):
        for c in range(3):
            val = state[r][c]
            if val != 0 and val != goal[r][c]:
                count += 1
    return count

def g_cost(state, goal):
    """g(n): số ô sai vị trí, không tính ô trống."""
    return misplaced_tiles(state, goal)

def h_cost(state, goal):
    """h(n): heuristic Manhattan."""
    return manhattan_distance(state, goal)

def f_cost(node, goal):
    """f(n): chi phí đánh giá dùng cho A*, f(n) = g(n) + h(n)."""
    return g_cost(node.state, goal) + h_cost(node.state, goal)
