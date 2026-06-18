# puzzle.py
import random
from utils import DIRS, DIR_MAP

class Puzzle:
    def __init__(self, start_state, goal_state):
        self.state = [row[:] for row in start_state]
        self.goal = goal_state
        self.size = len(start_state)
        self.empty_pos = self.find_empty(self.state)

    def find_empty(self, state):
        for r in range(self.size):
            for c in range(self.size):
                if state[r][c] == 0:
                    return (r, c)
        return (0, 0)

    def is_goal(self, state=None):
        if state is None:
            state = self.state
        return state == self.goal

    def get_neighbors(self, state):
        """Trả về danh sách các trạng thái hợp lệ tiếp theo."""
        neighbors = []
        r, c = self.find_empty(state)
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                new_state = [row[:] for row in state]
                # Hoán vị ô trống
                new_state[r][c], new_state[nr][nc] = new_state[nr][nc], new_state[r][c]
                neighbors.append((new_state, DIR_MAP[(dr, dc)]))
        return neighbors

    def move(self, direction):
        """Di chuyển trên bảng thực tế (ngược với logic ô trống)."""
        r, c = self.empty_pos
        nr, nc = r, c
        
        # Bấm mũi tên lên -> ô bên dưới đi lên -> ô trống lùi xuống
        if direction == "up": nr = r + 1
        elif direction == "down": nr = r - 1
        elif direction == "left": nc = c + 1
        elif direction == "right": nc = c - 1

        if 0 <= nr < self.size and 0 <= nc < self.size:
            self.state[r][c], self.state[nr][nc] = self.state[nr][nc], self.state[r][c]
            self.empty_pos = (nr, nc)
            return True
        return False