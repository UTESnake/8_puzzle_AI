# utils.py
import math

# Huong di chuyen cua o trong (delta row, delta column).
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
# Puzzle.move() nhan huong cua quan so/nguoi choi, nguoc voi huong o trong.
DIR_MAP = {(-1, 0): "down", (1, 0): "up", (0, -1): "right", (0, 1): "left"}


class SearchResult(list):
    """Danh sach buoc di kem thong tin ngan de UI ghi log."""

    def __init__(self, path, details=None):
        super().__init__(path)
        self.details = details or []


class Node:
    def __init__(self, state, parent=None, action=None, depth=0, h=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth
        self.g = depth
        self.h = h

    @property
    def f(self):
        return self.g + self.h

    def __lt__(self, other):
        if self.f != other.f:
            return self.f < other.f
        return self.g < other.g


def flatten_state(state):
    """Chuyen ma tran 2D hoac list/tuple 1D thanh tuple phang."""
    if not state:
        return tuple()
    if isinstance(state[0], (list, tuple)):
        return tuple(value for row in state for value in row)
    return tuple(state)


def board_size(state):
    if state and isinstance(state[0], (list, tuple)):
        return len(state)
    size = int(math.sqrt(len(state)))
    return size if size * size == len(state) else 3


def state_key(state):
    return flatten_state(state)


def extract_path(node):
    """Truy vet cac thao tac tu dich ve trang thai ban dau."""
    path = []
    curr = node
    while curr.parent is not None:
        path.append(curr.action)
        curr = curr.parent
    return path[::-1]


def inversion_count(state):
    values = [value for value in flatten_state(state) if value != 0]
    inversions = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            if values[i] > values[j]:
                inversions += 1
    return inversions


def is_solvable(state, goal=None):
    """Kiem tra trang thai co the di toi goal hay khong tren bang 3x3."""
    if goal is None:
        goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    return inversion_count(state) % 2 == inversion_count(goal) % 2


def manhattan_distance(state, goal):
    """h(n): tong khoang cach Manhattan tu state den goal."""
    state_flat = flatten_state(state)
    goal_flat = flatten_state(goal)
    size = board_size(goal)
    goal_pos = {}
    for index, value in enumerate(goal_flat):
        goal_pos[value] = divmod(index, size)

    dist = 0
    for index, value in enumerate(state_flat):
        if value != 0:
            r, c = divmod(index, size)
            gr, gc = goal_pos[value]
            dist += abs(r - gr) + abs(c - gc)
    return dist


def misplaced_tiles(state, goal):
    """Dem so o so sai vi tri, khong tinh o trong."""
    state_flat = flatten_state(state)
    goal_flat = flatten_state(goal)
    count = 0
    for value, target in zip(state_flat, goal_flat):
        if value != 0 and value != target:
            count += 1
    return count


def g_cost(node_or_state, goal=None):
    """g(n): chi phi duong di neu truyen Node; fallback cu la so o sai."""
    if isinstance(node_or_state, Node):
        return node_or_state.g
    if isinstance(node_or_state, int):
        return node_or_state
    return misplaced_tiles(node_or_state, goal)


def h_cost(state, goal):
    """h(n): heuristic Manhattan."""
    return manhattan_distance(state, goal)


def f_cost(node, goal):
    """f(n): chi phi danh gia dung cho A*, f(n) = g(n) + h(n)."""
    return node.g + h_cost(node.state, goal)
