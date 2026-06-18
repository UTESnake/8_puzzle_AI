# ui.py
import pygame
import sys
import random
import os
from grid import Puzzle
from algorithms_uninformed import bfs, dfs, ucs, iterative_deepening_search
from algorithms_informed import greedy, a_star, ida_star
from algorithms_local import (
    hill_climbing_simple,
    hill_climbing_steepest,
    hill_climbing_stochastic,
    hill_climbing_random_restart,
    local_beam_search,
    simulated_annealing,
)
from algorithms_complex import (
    search_without_start_state,
    partially_observable_search,
    and_or_search,
    backtracking_search,
)
from utils import g_cost, h_cost

# --- Constants & Colors ---
BG_APP = (242, 247, 246)
PANEL_BG = (252, 254, 253)
TEXT_DARK = (74, 83, 112)
TEXT_MID = (92, 111, 132)
TEXT_LIGHT = (135, 151, 170)
CELL_BLUE = (159, 204, 236)
CELL_GREEN = (166, 213, 165)
EMPTY_CELL_BG = (231, 239, 239)
BOARD_FRAME = (219, 239, 232)
BTN_AMBER = (245, 207, 94)
BTN_MINT = (117, 197, 165)
BTN_VIOLET = (181, 103, 207)
BTN_LAVENDER = (155, 146, 202)
BTN_CORAL = (231, 132, 96)
BTN_SKY = (112, 178, 222)
BTN_ROSE = (224, 113, 138)
BTN_LIME = (166, 204, 104)
BORDER_COLOR = (208, 224, 229)
WHITE = (255, 255, 255)

WIN_W, WIN_H = 1120, 835
GRID_SIZE, CELL_PX, GRID_PAD = 3, 68, 8
BOARD_W = GRID_SIZE * CELL_PX + (GRID_SIZE - 1) * GRID_PAD
GRID_START_X, GRID_START_Y = 90, 182
GOAL_START_X, GOAL_START_Y = 380, 182
PANEL_RECT = pygame.Rect(20, 10, 1080, 810)
LOG_RECT = pygame.Rect(695, 158, 360, 360)
SOLVE_DELAY_MS = 300

PLAYING_BOARD = [[0, 6, 5], [2, 1, 8], [7, 4, 3]]
GOAL_PATTERN  = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

# --- Fonts ---
pygame.init()

def make_font(size, bold=False):
    if sys.platform.startswith("win"):
        win_dir = os.environ.get("WINDIR", r"C:\Windows")
        font_file = "segoeuib.ttf" if bold else "segoeui.ttf"
        font_path = os.path.join(win_dir, "Fonts", font_file)
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)

    for name in ["Segoe UI", "Tahoma", "Arial", "Verdana"]:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f: return f
        except Exception: pass
    return pygame.font.Font(None, size + 4)

def make_named_font(name, size, bold=False):
    try:
        return pygame.font.SysFont(name, size, bold=bold)
    except Exception:
        return make_font(size, bold)

F_TITLE, F_MED, F_SM = make_font(32, bold=True), make_font(18), make_font(13)
F_NUMBER, F_ICON = make_font(30, bold=True), make_font(15, bold=True)
F_LABEL, F_HINT, F_STEPS = make_font(16, bold=True), make_font(15), make_font(24, bold=True)
F_LOG_TITLE, F_LOG, F_GROUP = make_named_font("Times New Roman", 14, bold=True), make_named_font("Times New Roman", 14), make_font(13, bold=True)
LOG_LINE_HEIGHT = 26
F_TITLE.set_italic(True)

def draw_button_icon(surf, kind, center, color=TEXT_DARK):
    x, y = center
    if kind == "shuffle":
        pygame.draw.arc(surf, color, (x - 9, y - 8, 18, 16), 0.3, 4.7, 2)
        pygame.draw.polygon(surf, color, [(x + 7, y - 7), (x + 12, y - 7), (x + 9, y - 2)])
    elif kind == "restart":
        pygame.draw.arc(surf, color, (x - 9, y - 9, 18, 18), 0.8, 5.8, 2)
        pygame.draw.polygon(surf, color, [(x - 8, y - 6), (x - 13, y - 5), (x - 10, y)])
    elif kind == "stop":
        pygame.draw.rect(surf, color, (x - 8, y - 8, 16, 16), 2, border_radius=3)
        pygame.draw.rect(surf, color, (x - 4, y - 4, 8, 8), border_radius=1)
    elif kind == "play":
        pygame.draw.polygon(surf, color, [(x - 6, y - 9), (x - 6, y + 9), (x + 9, y)])
    elif kind == "bfs":
        pts = [(x - 8, y - 5), (x, y - 5), (x + 8, y - 5), (x - 4, y + 6), (x + 4, y + 6)]
        for a, b in [(0, 3), (1, 3), (1, 4), (2, 4)]:
            pygame.draw.line(surf, color, pts[a], pts[b], 1)
        for pt in pts:
            pygame.draw.circle(surf, color, pt, 3)
    elif kind == "dfs":
        pts = [(x - 7, y - 7), (x - 2, y - 2), (x + 3, y + 3), (x + 8, y + 8)]
        pygame.draw.lines(surf, color, False, pts, 2)
        for pt in pts:
            pygame.draw.circle(surf, color, pt, 3)
    elif kind == "ucs":
        pygame.draw.circle(surf, color, (x, y), 8, 2)
        pygame.draw.line(surf, color, (x - 4, y), (x + 4, y), 2)
        pygame.draw.line(surf, color, (x, y - 5), (x, y + 5), 2)
    elif kind == "ids":
        for idx, width in enumerate((18, 14, 10)):
            top = y - 8 + idx * 6
            pygame.draw.rect(surf, color, (x - width // 2, top, width, 4), 1, border_radius=2)
        pygame.draw.line(surf, color, (x + 10, y - 8), (x + 10, y + 8), 2)
        pygame.draw.polygon(surf, color, [(x + 10, y + 8), (x + 6, y + 4), (x + 14, y + 4)])
    elif kind == "greedy":
        pygame.draw.circle(surf, color, (x, y), 8, 2)
        pygame.draw.circle(surf, color, (x, y), 3)
        pygame.draw.line(surf, color, (x + 4, y - 4), (x + 11, y - 11), 2)
    elif kind == "astar":
        pts = [(x, y - 10), (x + 3, y - 3), (x + 10, y - 3), (x + 5, y + 2), (x + 7, y + 9),
               (x, y + 5), (x - 7, y + 9), (x - 5, y + 2), (x - 10, y - 3), (x - 3, y - 3)]
        pygame.draw.polygon(surf, color, pts, 2)
    elif kind == "idastar":
        draw_button_icon(surf, "astar", (x - 2, y), color)
        pygame.draw.line(surf, color, (x + 9, y - 8), (x + 9, y + 8), 2)
        pygame.draw.polygon(surf, color, [(x + 9, y + 8), (x + 5, y + 4), (x + 13, y + 4)])
    elif kind == "hill":
        pygame.draw.lines(surf, color, False, [(x - 10, y + 8), (x - 3, y - 5), (x + 2, y + 1), (x + 8, y - 8), (x + 12, y + 8)], 2)
    elif kind == "steep":
        pygame.draw.lines(surf, color, False, [(x - 10, y + 8), (x - 2, y - 7), (x + 10, y + 8)], 2)
        pygame.draw.line(surf, color, (x - 5, y + 4), (x + 4, y - 5), 2)
        pygame.draw.polygon(surf, color, [(x + 4, y - 5), (x + 1, y - 5), (x + 4, y - 8)])
    elif kind == "random":
        pygame.draw.rect(surf, color, (x - 8, y - 8, 16, 16), 2, border_radius=3)
        for pt in [(x - 4, y - 4), (x + 4, y - 4), (x, y), (x - 4, y + 4), (x + 4, y + 4)]:
            pygame.draw.circle(surf, color, pt, 1)
    elif kind == "restart_hill":
        draw_button_icon(surf, "hill", (x, y), color)
        pygame.draw.arc(surf, color, (x - 12, y - 12, 24, 20), 0.0, 2.7, 2)
        pygame.draw.polygon(surf, color, [(x + 9, y - 8), (x + 13, y - 5), (x + 8, y - 3)])
    elif kind == "beam":
        pygame.draw.circle(surf, color, (x - 8, y), 3)
        for end in [(x + 9, y - 8), (x + 11, y), (x + 9, y + 8)]:
            pygame.draw.line(surf, color, (x - 4, y), end, 2)
    elif kind == "anneal":
        pygame.draw.line(surf, color, (x - 10, y + 7), (x + 10, y + 7), 2)
        pygame.draw.lines(
            surf, color, False,
            [(x - 8, y + 5), (x - 5, y - 5), (x, y + 1), (x + 4, y - 9), (x + 8, y + 5)],
            2,
        )
    elif kind == "uncertain":
        pygame.draw.circle(surf, color, (x, y), 9, 2)
        mark = F_ICON.render("?", True, color)
        surf.blit(mark, mark.get_rect(center=(x, y - 1)))
    elif kind == "partial":
        pygame.draw.arc(surf, color, (x - 11, y - 7, 22, 14), 0, 3.14, 2)
        pygame.draw.circle(surf, color, (x, y), 3, 2)
        pygame.draw.line(surf, color, (x - 10, y + 8), (x + 10, y - 8), 2)
    elif kind == "andor":
        pygame.draw.circle(surf, color, (x - 8, y), 3)
        pygame.draw.circle(surf, color, (x + 8, y - 7), 3)
        pygame.draw.circle(surf, color, (x + 8, y + 7), 3)
        pygame.draw.line(surf, color, (x - 5, y), (x + 5, y - 6), 2)
        pygame.draw.line(surf, color, (x - 5, y), (x + 5, y + 6), 2)
    elif kind == "backtrack":
        pygame.draw.lines(
            surf, color, False,
            [(x - 9, y - 7), (x + 6, y - 7), (x + 6, y + 5), (x - 4, y + 5)],
            2,
        )
        pygame.draw.polygon(surf, color, [(x - 4, y + 5), (x + 1, y + 1), (x + 1, y + 9)])
    else:
        label = F_ICON.render(str(kind)[:1], True, color)
        surf.blit(label, label.get_rect(center=center))

class Btn:
    def __init__(self, rect, text, bg_color, icon_kind=""):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bg_color = bg_color
        self.icon_kind = icon_kind
        self.hovered = False

    def draw(self, surf):
        color = self.bg_color
        if self.hovered:
            color = tuple(min(255, c + 12) for c in color)
        shadow = self.rect.move(0, 3)
        shadow_color = tuple(max(0, int(c * 0.72)) for c in self.bg_color)
        pygame.draw.rect(surf, shadow_color, shadow, border_radius=9)
        pygame.draw.rect(surf, color, self.rect, border_radius=9)
        pygame.draw.rect(surf, (255, 255, 255), self.rect.inflate(-2, -2), 1, border_radius=8)
        pygame.draw.rect(surf, tuple(max(0, c - 28) for c in self.bg_color), self.rect, 1, border_radius=9)
        
        lbl_text = F_SM.render(self.text, True, TEXT_DARK)
        text_rect = lbl_text.get_rect(center=self.rect.center)
        if self.icon_kind:
            icon_center = (text_rect.left - 12, text_rect.centery)
            draw_button_icon(surf, self.icon_kind, icon_center, TEXT_DARK)
            text_rect.centerx += 10
        surf.blit(lbl_text, text_rect)

    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def is_clicked(self, ev):
        return (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.rect.collidepoint(ev.pos))

class PuzzleApp:
    def __init__(self):
        # Mở toàn màn hình và để Pygame tự co giãn giao diện từ kích thước
        # thiết kế 1120x835 sang đúng độ phân giải màn hình hiện tại.
        self.screen = pygame.display.set_mode(
            (WIN_W, WIN_H),
            pygame.FULLSCREEN | pygame.SCALED,
        )
        pygame.display.set_caption("8-Puzzle Numbers")
        self.clock = pygame.time.Clock()
        
        self.puzzle = Puzzle(PLAYING_BOARD, GOAL_PATTERN)
        self.num_steps = 0
        self.animating_path = []
        self.last_anim_time = 0
        self.active_algo = ""
        self.animation_total = 0
        self.paused = False
        self.logs = ["Sẵn sàng."]
        self.log_scroll = 0
        self.log_dragging = False
        self.log_drag_offset = 0
        self.notice_text = ""
        self.notice_until = 0

        # Khởi tạo Nút
        self.btns = {
            'shuffle': Btn((134, 488, 132, 38), "Xáo Trộn", BTN_AMBER, "shuffle"),
            'restart': Btn((286, 488, 132, 38), "Chơi Lại", BTN_LIME, "restart"),
            'stop': Btn((438, 488, 132, 38), "Dừng Lại", BTN_ROSE, "stop"),
            'bfs': Btn((62, 566, 130, 36), "BFS", BTN_MINT, "bfs"),
            'dfs': Btn((208, 566, 130, 36), "DFS", BTN_VIOLET, "dfs"),
            'ids': Btn((354, 566, 130, 36), "IDS", BTN_SKY, "ids"),
            'ucs': Btn((500, 566, 130, 36), "UCS", BTN_LAVENDER, "ucs"),
            'greedy': Btn((682, 566, 110, 36), "Greedy", BTN_AMBER, "greedy"),
            'astar': Btn((806, 566, 110, 36), "A*", BTN_CORAL, "astar"),
            'idastar': Btn((930, 566, 110, 36), "IDA*", BTN_LAVENDER, "idastar"),
            'hill_simple': Btn((62, 666, 150, 34), "Simple", BTN_MINT, "hill"),
            'hill_steepest': Btn((236, 666, 150, 34), "Steepest", BTN_VIOLET, "steep"),
            'hill_stochastic': Btn((410, 666, 150, 34), "Stochastic", BTN_LAVENDER, "random"),
            'hill_restart': Btn((584, 666, 150, 34), "Restart", BTN_AMBER, "restart_hill"),
            'beam': Btn((758, 666, 150, 34), "Beam", BTN_CORAL, "beam"),
            'annealing': Btn((932, 666, 110, 34), "Annealing", BTN_SKY, "anneal"),
            'no_start': Btn((66, 766, 225, 34), "Không trạng thái đầu", BTN_AMBER, "uncertain"),
            'partial': Btn((316, 766, 210, 34), "Nhìn thấy một phần", BTN_MINT, "partial"),
            'and_or': Btn((551, 766, 190, 34), "AND-OR Search", BTN_VIOLET, "andor"),
            'backtracking': Btn((766, 766, 260, 34), "Backtracking", BTN_CORAL, "backtrack"),
        }
        self.algorithms = {
            'bfs': (bfs, "BFS"),
            'dfs': (dfs, "DFS"),
            'ucs': (ucs, "UCS"),
            'ids': (iterative_deepening_search, "IDS"),
            'greedy': (greedy, "Greedy"),
            'astar': (a_star, "A*"),
            'idastar': (ida_star, "IDA*"),
            'hill_simple': (hill_climbing_simple, "Simple Hill"),
            'hill_steepest': (hill_climbing_steepest, "Steepest Hill"),
            'hill_stochastic': (hill_climbing_stochastic, "Stochastic Hill"),
            'hill_restart': (hill_climbing_random_restart, "Random Restart"),
            'beam': (local_beam_search, "Local Beam"),
            'annealing': (simulated_annealing, "Simulated Annealing"),
            'no_start': (search_without_start_state, "Không trạng thái đầu"),
            'partial': (partially_observable_search, "Nhìn thấy một phần"),
            'and_or': (and_or_search, "AND-OR Search"),
            'backtracking': (backtracking_search, "Backtracking"),
        }
        self.uninformed_labels = {"BFS", "DFS", "UCS", "IDS"}
        self.cost_modes = {
            "UCS": "g",
            "Greedy": "h",
            "A*": "f",
            "IDA*": "f",
            "Simple Hill": "h",
            "Steepest Hill": "h",
            "Stochastic Hill": "h",
            "Random Restart": "h",
            "Local Beam": "h",
            "Simulated Annealing": "h",
            "Không trạng thái đầu": "h",
            "Nhìn thấy một phần": "h",
            "AND-OR Search": "h",
            "Backtracking": "h",
        }

    def draw_soft_rect(self, rect, color, radius=18, border=None):
        shadow = pygame.Rect(rect).move(0, 5)
        pygame.draw.rect(self.screen, (226, 234, 236), shadow, border_radius=radius)
        pygame.draw.rect(self.screen, color, rect, border_radius=radius)
        if border:
            pygame.draw.rect(self.screen, border, rect, 1, border_radius=radius)

    def draw_centered_text(self, text, font, color, center, icon_gap=0):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=center)
        rect.x += icon_gap
        self.screen.blit(surf, rect)

    def add_log(self, text):
        was_at_bottom = self.log_scroll == 0
        self.logs.append(text)
        if was_at_bottom:
            self.log_scroll = 0
        else:
            self.log_scroll += 1
        self.clamp_log_scroll()

    def show_notice(self, text, duration=2500):
        self.notice_text = text
        self.notice_until = pygame.time.get_ticks() + duration

    def log_visible_count(self):
        return max(1, (LOG_RECT.height - 42) // LOG_LINE_HEIGHT)

    def max_log_scroll(self):
        return max(0, len(self.logs) - self.log_visible_count())

    def clamp_log_scroll(self):
        self.log_scroll = max(0, min(self.log_scroll, self.max_log_scroll()))

    def log_scrollbar_rect(self):
        visible = self.log_visible_count()
        total = len(self.logs)
        track = pygame.Rect(LOG_RECT.right - 14, LOG_RECT.y + 34, 6, LOG_RECT.height - 48)
        if total <= visible:
            return track, None

        thumb_h = max(28, int(track.height * visible / total))
        scrollable = max(1, track.height - thumb_h)
        thumb_y = track.bottom - thumb_h - int(scrollable * self.log_scroll / self.max_log_scroll())
        return track, pygame.Rect(track.x, thumb_y, track.width, thumb_h)

    def set_log_scroll_from_mouse(self, mouse_y):
        track, thumb = self.log_scrollbar_rect()
        if thumb is None:
            self.log_scroll = 0
            return

        top = track.y + self.log_drag_offset
        bottom = track.bottom - thumb.height + self.log_drag_offset
        thumb_y = max(top, min(mouse_y, bottom)) - self.log_drag_offset
        ratio = (track.bottom - thumb.height - thumb_y) / max(1, track.height - thumb.height)
        self.log_scroll = round(ratio * self.max_log_scroll())
        self.clamp_log_scroll()

    def get_moving_tile(self, direction):
        r, c = self.puzzle.empty_pos
        nr, nc = r, c
        if direction == "up":
            nr = r + 1
        elif direction == "down":
            nr = r - 1
        elif direction == "left":
            nc = c + 1
        elif direction == "right":
            nc = c - 1

        if 0 <= nr < self.puzzle.size and 0 <= nc < self.puzzle.size:
            return self.puzzle.state[nr][nc]
        return None

    def move_and_log(self, direction, source="Bạn"):
        tile = self.get_moving_tile(direction)
        if tile is None or not self.puzzle.move(direction):
            return False

        self.num_steps += 1
        arrows = {"up": "↑", "down": "↓", "left": "←", "right": "→"}
        self.add_log(f"{source}: {self.num_steps}. Ô {tile} {arrows[direction]}")
        return True

    def add_cost_log(self, label):
        g_value = g_cost(self.puzzle.state, self.puzzle.goal)
        h_value = h_cost(self.puzzle.state, self.puzzle.goal)
        mode = self.cost_modes.get(label)
        if mode == "g":
            self.add_log(f"g(n)={g_value} ô sai")
        elif mode == "h":
            self.add_log(f"h(n)={h_value}")
        elif mode == "f":
            self.add_log(f"f(n)=g(n)+h(n)={g_value}+{h_value}={g_value + h_value}")

    def should_log_cost(self, label):
        return label in self.cost_modes

    def draw_puzzle_icon(self, center, size=24, color=TEXT_DARK):
        rect = pygame.Rect(0, 0, size, size)
        rect.center = center
        pygame.draw.rect(self.screen, color, rect, 2, border_radius=4)
        pygame.draw.line(self.screen, color, (rect.centerx, rect.top + 4), (rect.centerx, rect.bottom - 4), 2)
        pygame.draw.line(self.screen, color, (rect.left + 4, rect.centery), (rect.right - 4, rect.centery), 2)
        pygame.draw.circle(self.screen, PANEL_BG, (rect.centerx, rect.top), 4)

    def draw_cube_icon(self, center, color=TEXT_DARK):
        x, y = center
        front = [(x - 12, y - 8), (x, y - 14), (x + 12, y - 8), (x, y - 1)]
        left = [(x - 12, y - 8), (x, y - 1), (x, y + 14), (x - 12, y + 6)]
        right = [(x + 12, y - 8), (x, y - 1), (x, y + 14), (x + 12, y + 6)]
        pygame.draw.polygon(self.screen, color, front, 2)
        pygame.draw.polygon(self.screen, color, left, 2)
        pygame.draw.polygon(self.screen, color, right, 2)
        pygame.draw.circle(self.screen, color, (x - 4, y - 7), 2)
        pygame.draw.circle(self.screen, color, (x + 5, y - 7), 2)
        pygame.draw.circle(self.screen, color, (x - 5, y + 5), 2)
        pygame.draw.circle(self.screen, color, (x + 5, y + 7), 2)

    def draw_clock_icon(self, center, color=TEXT_DARK):
        pygame.draw.circle(self.screen, color, center, 13, 2)
        pygame.draw.line(self.screen, color, center, (center[0], center[1] - 8), 2)
        pygame.draw.line(self.screen, color, center, (center[0] + 7, center[1] + 3), 2)
        pygame.draw.circle(self.screen, color, (center[0] - 9, center[1] - 13), 4, 2)
        pygame.draw.circle(self.screen, color, (center[0] + 9, center[1] - 13), 4, 2)

    def draw_header_clock_icon(self, center, color=TEXT_DARK):
        x, y = center
        pygame.draw.circle(self.screen, color, center, 15, 3)
        pygame.draw.line(self.screen, color, center, (x, y - 9), 3)
        pygame.draw.line(self.screen, color, center, (x + 8, y + 4), 3)
        pygame.draw.arc(self.screen, color, (x - 20, y - 22, 14, 12), 3.3, 6.0, 3)
        pygame.draw.arc(self.screen, color, (x + 6, y - 22, 14, 12), 3.4, 6.1, 3)
        pygame.draw.line(self.screen, color, (x - 8, y + 14), (x - 13, y + 20), 3)
        pygame.draw.line(self.screen, color, (x + 8, y + 14), (x + 13, y + 20), 3)

    def draw_arrow_keys_hint(self, center_y):
        prefix = F_MED.render("Dùng các phím mũi tên", True, TEXT_LIGHT)
        suffix = F_MED.render("để di chuyển", True, TEXT_LIGHT)
        key_w, key_h, gap = 24, 24, 5
        keys_w = key_w * 4 + gap * 3
        total_w = prefix.get_width() + 18 + keys_w + 18 + suffix.get_width()
        x = WIN_W // 2 - total_w // 2

        self.screen.blit(prefix, (x, center_y - prefix.get_height() // 2))
        x += prefix.get_width() + 18

        for arrow in ["←", "↑", "↓", "→"]:
            rect = pygame.Rect(x, center_y - key_h // 2, key_w, key_h)
            pygame.draw.rect(self.screen, (248, 251, 250), rect, border_radius=5)
            pygame.draw.rect(self.screen, (178, 194, 207), rect, 2, border_radius=5)
            label = F_SM.render(arrow, True, TEXT_MID)
            self.screen.blit(label, label.get_rect(center=rect.center))
            x += key_w + gap

        x += 18 - gap
        self.screen.blit(suffix, (x, center_y - suffix.get_height() // 2))

    def draw_small_icon(self, kind, center, color=TEXT_MID):
        x, y = center
        if kind == "board":
            rect = pygame.Rect(x - 7, y - 7, 14, 14)
            pygame.draw.rect(self.screen, color, rect, 2, border_radius=2)
            pygame.draw.line(self.screen, color, (x, y - 6), (x, y + 6), 2)
            pygame.draw.line(self.screen, color, (x - 6, y), (x + 6, y), 2)
        elif kind == "goal":
            pygame.draw.circle(self.screen, color, (x, y), 8, 2)
            pygame.draw.circle(self.screen, color, (x, y), 3)
        elif kind == "steps":
            pygame.draw.circle(self.screen, color, (x - 5, y), 5)
            pygame.draw.circle(self.screen, color, (x + 5, y), 5)
            pygame.draw.circle(self.screen, color, (x, y - 6), 5)
            pygame.draw.rect(self.screen, color, (x - 2, y, 4, 11), border_radius=2)
        elif kind == "log":
            pygame.draw.rect(self.screen, color, (x - 8, y - 8, 16, 16), 2, border_radius=3)
            for offset in (-4, 0, 4):
                pygame.draw.line(self.screen, color, (x - 4, y + offset), (x + 5, y + offset), 1)

    def draw_log(self):
        pygame.draw.rect(self.screen, (241, 247, 247), LOG_RECT, border_radius=10)
        pygame.draw.rect(self.screen, (214, 230, 232), LOG_RECT, 1, border_radius=10)
        self.draw_small_icon("log", (LOG_RECT.x + 18, LOG_RECT.y + 17), TEXT_MID)
        title = F_LOG_TITLE.render("Log", True, TEXT_MID)
        self.screen.blit(title, (LOG_RECT.x + 34, LOG_RECT.y + 8))

        visible = self.log_visible_count()
        start = max(0, len(self.logs) - visible - self.log_scroll)
        end = min(len(self.logs), start + visible)
        max_width = LOG_RECT.width - (44 if len(self.logs) > visible else 28)

        for idx, line in enumerate(self.logs[start:end]):
            line = self.trim_log_line(line, max_width)
            log_line = F_LOG.render(line, True, TEXT_LIGHT)
            self.screen.blit(log_line, (LOG_RECT.x + 14, LOG_RECT.y + 34 + idx * LOG_LINE_HEIGHT))

        track, thumb = self.log_scrollbar_rect()
        if thumb:
            pygame.draw.rect(self.screen, (220, 232, 234), track, border_radius=4)
            pygame.draw.rect(self.screen, TEXT_LIGHT, thumb, border_radius=4)

    def trim_log_line(self, text, max_width):
        if F_LOG.size(text)[0] <= max_width:
            return text

        suffix = "..."
        lo, hi = 0, len(text)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if F_LOG.size(text[:mid] + suffix)[0] <= max_width:
                lo = mid
            else:
                hi = mid - 1
        return text[:lo] + suffix

    def draw_algorithm_groups(self):
        groups = [
            ("Tìm kiếm không thông tin", pygame.Rect(46, 532, 600, 82)),
            ("Tìm kiếm có thông tin", pygame.Rect(666, 532, 390, 82)),
            ("Tìm kiếm cục bộ", pygame.Rect(46, 632, 1010, 76)),
            ("Tìm kiếm trong môi trường phức tạp", pygame.Rect(46, 732, 1010, 76)),
        ]

        for title, rect in groups:
            pygame.draw.rect(self.screen, (247, 251, 250), rect, border_radius=10)
            pygame.draw.rect(self.screen, (219, 232, 233), rect, 1, border_radius=10)
            label = F_GROUP.render(title, True, TEXT_MID)
            self.screen.blit(label, (rect.x + 12, rect.y + 7))

    def draw_notice(self):
        if not self.notice_text or pygame.time.get_ticks() >= self.notice_until:
            return

        notice = F_LABEL.render(self.notice_text, True, TEXT_DARK)
        rect = notice.get_rect(center=(WIN_W // 2, 128))
        box = rect.inflate(36, 18)
        pygame.draw.rect(self.screen, (255, 236, 205), box, border_radius=10)
        pygame.draw.rect(self.screen, (231, 182, 126), box, 1, border_radius=10)
        self.screen.blit(notice, rect)

    def draw_board(self, state, start_x, start_y, is_goal=False):
        board_rect = pygame.Rect(start_x - 14, start_y - 14, BOARD_W + 28, BOARD_W + 28)
        pygame.draw.rect(self.screen, BOARD_FRAME, board_rect, border_radius=14)
        pygame.draw.rect(self.screen, (191, 225, 218), board_rect, 2, border_radius=14)

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                val = state[r][c]
                px = start_x + c * (CELL_PX + GRID_PAD)
                py = start_y + r * (CELL_PX + GRID_PAD)
                rect = pygame.Rect(px, py, CELL_PX, CELL_PX)
                
                if val == 0:
                    bg_color, text_color = EMPTY_CELL_BG, EMPTY_CELL_BG
                else:
                    bg_color = CELL_GREEN if is_goal else CELL_BLUE
                    text_color = WHITE
                
                shadow = rect.move(3, 4)
                pygame.draw.rect(self.screen, (135, 165, 188) if not is_goal else (132, 174, 130), shadow, border_radius=8)
                pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
                pygame.draw.rect(self.screen, BORDER_COLOR, rect, 1, border_radius=8)
                
                if val != 0:
                    lbl = F_NUMBER.render(str(val), True, text_color)
                    self.screen.blit(lbl, lbl.get_rect(center=rect.center))

    def draw_ui(self):
        self.screen.fill(PANEL_BG)
        pygame.draw.rect(self.screen, PANEL_BG, PANEL_RECT, border_radius=22)

        title_shadow = F_TITLE.render("8-Puzzle Numbers", True, (196, 207, 218))
        title = F_TITLE.render("8-Puzzle Numbers", True, TEXT_DARK)
        title_rect = title.get_rect(center=(WIN_W // 2, 64))
        self.screen.blit(title_shadow, title_rect.move(3, 3))
        self.screen.blit(title, title_rect)
        self.draw_cube_icon((title_rect.left - 42, title_rect.centery + 1), TEXT_DARK)
        self.draw_header_clock_icon((title_rect.right + 42, title_rect.centery + 1), TEXT_DARK)
        self.draw_arrow_keys_hint(106)
        self.draw_notice()

        self.draw_small_icon("board", (GRID_START_X + 8, 146), TEXT_MID)
        self.screen.blit(F_LABEL.render("Bảng Chơi", True, TEXT_MID), (GRID_START_X + 24, 136))
        self.draw_board(self.puzzle.state, GRID_START_X, GRID_START_Y)

        self.draw_small_icon("goal", (GOAL_START_X + 8, 146), TEXT_MID)
        self.screen.blit(F_LABEL.render("Hình Mẫu", True, TEXT_MID), (GOAL_START_X + 24, 136))
        self.draw_board(self.puzzle.goal, GOAL_START_X, GOAL_START_Y, is_goal=True)

        guide_1 = F_HINT.render("Hãy sắp xếp các số", True, TEXT_MID)
        guide_2 = F_HINT.render("giống với hình mẫu nhé!", True, TEXT_MID)
        self.screen.blit(guide_1, guide_1.get_rect(center=(GOAL_START_X + BOARD_W // 2, 442)))
        self.screen.blit(guide_2, guide_2.get_rect(center=(GOAL_START_X + BOARD_W // 2, 464)))

        steps = F_STEPS.render(f"Số Bước: {self.num_steps}", True, TEXT_DARK)
        steps_rect = steps.get_rect(center=(GRID_START_X + BOARD_W // 2 + 18, 432))
        self.draw_small_icon("steps", (steps_rect.left - 24, steps_rect.centery - 1), TEXT_DARK)
        self.screen.blit(steps, steps_rect)

        self.draw_log()

        self.draw_algorithm_groups()
        for btn in self.btns.values():
            btn.draw(self.screen)

    def set_pause_button(self, paused):
        self.btns["stop"].text = "Tiếp Tục" if paused else "Dừng Lại"
        self.btns["stop"].icon_kind = "play" if paused else "stop"

    def toggle_pause(self):
        if not self.animating_path:
            self.paused = False
            self.set_pause_button(False)
            self.add_log("Không có thuật toán đang chạy.")
            return

        self.paused = not self.paused
        self.set_pause_button(self.paused)
        if self.paused:
            self.add_log(f"{self.active_algo}: đã tạm dừng.")
        else:
            self.last_anim_time = pygame.time.get_ticks()
            self.add_log(f"{self.active_algo}: tiếp tục.")

    def restart_game(self):
        self.puzzle = Puzzle(PLAYING_BOARD, GOAL_PATTERN)
        self.num_steps = 0
        self.animating_path = []
        self.active_algo = ""
        self.animation_total = 0
        self.paused = False
        self.set_pause_button(False)
        self.add_log("Đã chơi lại.")

    def shuffle_game(self):
        self.animating_path = []
        self.active_algo = ""
        self.animation_total = 0
        self.paused = False
        self.set_pause_button(False)
        for _ in range(50):
            self.puzzle.move(random.choice(["up", "down", "left", "right"]))
        self.num_steps = 0
        self.add_log("Đã xáo trộn bảng.")

    def solve_and_animate(self, algo_func, label):
        path = algo_func(self.puzzle)
        if path is not None:
            details = getattr(path, "details", [])
            self.animating_path = list(path)
            self.active_algo = label
            self.animation_total = len(path)
            self.paused = False
            self.set_pause_button(False)
            self.last_anim_time = pygame.time.get_ticks()
            self.add_log(f"{label}: tìm thấy {len(path)} bước.")
            for detail in details:
                self.add_log(f"{label}: {detail}")
            if self.should_log_cost(label):
                self.add_cost_log(label)
            if not path:
                if self.puzzle.is_goal():
                    self.add_log("Bảng đã đúng hình mẫu.")
                else:
                    self.add_log(f"{label}: dừng tại cực trị.")
                self.active_algo = ""
                self.set_pause_button(False)
        else:
            if label in self.uninformed_labels:
                message = f"{label}: không giải được."
            else:
                message = f"{label}: không tìm thấy lời giải."
            self.add_log(message)
            self.show_notice(message)

    def run(self):
        while True:
            mpos = pygame.mouse.get_pos()
            for btn in self.btns.values():
                btn.update_hover(mpos)
                
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                if ev.type == pygame.MOUSEWHEEL and LOG_RECT.collidepoint(pygame.mouse.get_pos()):
                    self.log_scroll += ev.y * 3
                    self.clamp_log_scroll()

                if ev.type == pygame.MOUSEBUTTONDOWN and LOG_RECT.collidepoint(ev.pos):
                    if ev.button == 1:
                        track, thumb = self.log_scrollbar_rect()
                        if thumb and thumb.collidepoint(ev.pos):
                            self.log_dragging = True
                            self.log_drag_offset = ev.pos[1] - thumb.y
                        elif thumb and track.collidepoint(ev.pos):
                            page = self.log_visible_count()
                            self.log_scroll += page if ev.pos[1] < thumb.y else -page
                            self.clamp_log_scroll()
                    elif ev.button == 4:
                        self.log_scroll += 3
                        self.clamp_log_scroll()
                    elif ev.button == 5:
                        self.log_scroll -= 3
                        self.clamp_log_scroll()

                if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                    self.log_dragging = False

                if ev.type == pygame.MOUSEMOTION and self.log_dragging:
                    self.set_log_scroll_from_mouse(ev.pos[1])
                
                if ev.type == pygame.KEYDOWN and not self.animating_path:
                    if ev.key == pygame.K_UP: self.move_and_log("up")
                    elif ev.key == pygame.K_DOWN: self.move_and_log("down")
                    elif ev.key == pygame.K_LEFT: self.move_and_log("left")
                    elif ev.key == pygame.K_RIGHT: self.move_and_log("right")

                if self.btns['stop'].is_clicked(ev):
                    self.toggle_pause()

                if self.btns['restart'].is_clicked(ev):
                    self.restart_game()
                    continue

                if self.btns['shuffle'].is_clicked(ev):
                    self.shuffle_game()
                    continue

                if not self.animating_path:
                    for key, (algo_func, label) in self.algorithms.items():
                        if self.btns[key].is_clicked(ev):
                            self.solve_and_animate(algo_func, label)
                            break

            # Xử lý Animation Tự động giải
            if self.animating_path and not self.paused:
                now = pygame.time.get_ticks()
                if now - self.last_anim_time > SOLVE_DELAY_MS:
                    step = self.animating_path.pop(0)
                    current = self.animation_total - len(self.animating_path)
                    self.move_and_log(step, f"{self.active_algo} {current}/{self.animation_total}")
                    if self.should_log_cost(self.active_algo):
                        self.add_cost_log(self.active_algo)
                    self.last_anim_time = now
                    if not self.animating_path:
                        if self.puzzle.is_goal():
                            self.add_log(f"{self.active_algo}: hoàn thành.")
                        else:
                            self.add_log(f"{self.active_algo}: chưa đạt đích.")
                        self.active_algo = ""
                        self.paused = False
                        self.set_pause_button(False)

            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)
