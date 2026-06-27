"""Adversarial and stochastic search demos.

The 8-puzzle is a deterministic single-player problem.  To match the
reference zip, Minimax, Alpha-Beta, and Expectimax are demonstrated on a
small Caro board instead of pretending the puzzle has an opponent.
"""

import math
import random
import time

from utils import SearchResult


CARO_START = ("X", "O", "X", ".", "O", ".", ".", ".", ".")
CARO_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def _board_text(board):
    rows = [" ".join(board[index : index + 3]) for index in range(0, 9, 3)]
    return " / ".join(rows)


def _winner_text(winner):
    if winner == "X":
        return "X thắng"
    if winner == "O":
        return "O thắng"
    if winner == "Draw":
        return "Hòa"
    return "Chưa kết thúc"


def _winner(board):
    for a, b, c in CARO_LINES:
        if board[a] != "." and board[a] == board[b] == board[c]:
            return board[a]
    if "." not in board:
        return "Draw"
    return None


def _moves(board):
    return [index for index, cell in enumerate(board) if cell == "."]


def _apply(board, move, player):
    cells = list(board)
    cells[move] = player
    return tuple(cells)


def _action(move, player):
    row, col = divmod(move, 3)
    return f"{player}@{row + 1},{col + 1}"


def _children(board, player, rng):
    children = [(_action(move, player), _apply(board, move, player)) for move in _moves(board)]
    if len(children) > 1:
        rng.shuffle(children)
    return children


def _utility(board, ply):
    winner = _winner(board)
    if winner == "X":
        return 100.0 - ply
    if winner == "O":
        return ply - 100.0
    if winner == "Draw":
        return 0.0

    score = 0.0
    for line in CARO_LINES:
        cells = [board[index] for index in line]
        x_count = cells.count("X")
        o_count = cells.count("O")
        if x_count and o_count:
            continue
        if x_count:
            score += 1.5 * x_count
        if o_count:
            score -= 1.5 * o_count
    return score - 0.01 * ply


def _demo_result(
    algorithm,
    actions,
    step_boards,
    final_score,
    final_board,
    winner,
    nodes_expanded,
    nodes_generated,
    max_frontier_size,
    runtime_ms,
    details,
    summary_lines=None,
):
    result = SearchResult([], details)
    result.demo_only = True
    result.demo_initial_board = CARO_START
    result.demo_board = final_board
    result.demo_steps = [
        {"action": action, "board": board}
        for action, board in zip(actions, step_boards)
    ]
    result.demo_winner = winner
    result.actions = actions
    result.message = f"hoàn tất Caro: {_winner_text(winner)} sau {len(actions)} nước."
    result.summary_lines = summary_lines or [
        f"Kết quả: {_winner_text(winner)}",
        f"Số nước: {len(actions)}",
        f"Node: {nodes_expanded} mở / {nodes_generated} sinh",
    ]
    result.algorithm = algorithm
    result.group = "Adversarial Search"
    result.path_cost = len(actions)
    result.nodes_expanded = nodes_expanded
    result.nodes_generated = nodes_generated
    result.max_frontier_size = max_frontier_size
    result.runtime_ms = runtime_ms
    return result


def _minimax_like(algorithm, max_depth, seed=None):
    rng = random.Random(seed)
    start_time = time.perf_counter()
    depth_limit = max(1, min(6, max_depth))
    nodes_expanded = 0
    nodes_generated = 1
    pruned = 0

    def value(board, depth, maximizing, alpha, beta):
        nonlocal nodes_expanded, nodes_generated, pruned
        if depth == 0 or _winner(board) is not None:
            return _utility(board, depth_limit - depth)

        player = "X" if maximizing else "O"
        children = _children(board, player, rng)
        nodes_expanded += 1
        nodes_generated += len(children)

        if maximizing:
            best = -math.inf
            for index, (_child_action, child) in enumerate(children):
                best = max(best, value(child, depth - 1, False, alpha, beta))
                if algorithm == "Alpha-Beta":
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        pruned += len(children) - index - 1
                        break
            return best

        best = math.inf
        for index, (_child_action, child) in enumerate(children):
            best = min(best, value(child, depth - 1, True, alpha, beta))
            if algorithm == "Alpha-Beta":
                beta = min(beta, best)
                if beta <= alpha:
                    pruned += len(children) - index - 1
                    break
        return best

    def choose_move(board, player):
        children = _children(board, player, rng)
        if not children:
            return _utility(board, 0), None, board

        maximizing = player == "X"
        scored = []
        for action, child in children:
            score = value(
                child,
                depth_limit - 1,
                not maximizing,
                -math.inf,
                math.inf,
            )
            scored.append((score, action, child))

        if maximizing:
            return max(scored, key=lambda item: (item[0], item[1]))
        return min(scored, key=lambda item: (item[0], item[1]))

    board = CARO_START
    player = "X"
    actions = []
    step_boards = []
    final_score = _utility(board, 0)
    max_frontier_size = 1

    while _winner(board) is None:
        score, action, next_board = choose_move(board, player)
        if action is None:
            break
        actions.append(action)
        board = next_board
        step_boards.append(board)
        final_score = score
        max_frontier_size = max(max_frontier_size, len(_moves(board)))
        player = "O" if player == "X" else "X"

    winner = _winner(board)

    runtime_ms = (time.perf_counter() - start_time) * 1000
    details = [
        "Demo Caro 3x3: MAX=X, MIN=O.",
        f"Start: {_board_text(CARO_START)}",
        f"Moves: {' -> '.join(actions) if actions else 'No move'}",
        f"Final: {_board_text(board)}",
        f"Result: {_winner_text(winner)}; moves: {len(actions)}.",
        f"Depth limit: {depth_limit}; final utility: {final_score:.2f}.",
        f"Expanded: {nodes_expanded}; generated: {nodes_generated}.",
    ]
    if algorithm == "Alpha-Beta":
        details.append(f"Pruned branches: {pruned}.")

    return _demo_result(
        algorithm=algorithm,
        actions=actions,
        step_boards=step_boards,
        final_score=final_score,
        final_board=board,
        winner=winner,
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        max_frontier_size=max_frontier_size,
        runtime_ms=runtime_ms,
        details=details,
        summary_lines=[
            f"Kết quả: {_winner_text(winner)}",
            f"Số nước: {len(actions)}",
            (
                f"Node: {nodes_expanded}/{nodes_generated} | Cắt: {pruned}"
                if algorithm == "Alpha-Beta"
                else f"Node: {nodes_expanded} mở / {nodes_generated} sinh"
            ),
        ],
    )


def minimax_search(_puzzle=None, max_depth=4, seed=None):
    return _minimax_like("Minimax", max_depth=max_depth, seed=seed)


def alpha_beta_search(_puzzle=None, max_depth=6, seed=None):
    return _minimax_like("Alpha-Beta", max_depth=max_depth, seed=seed)


def expectimax_search(_puzzle=None, max_depth=4, seed=None):
    rng = random.Random(seed)
    start_time = time.perf_counter()
    depth_limit = max(1, min(6, max_depth))
    nodes_expanded = 0
    nodes_generated = 1

    def expected_value(board, depth, maximizing):
        nonlocal nodes_expanded, nodes_generated
        if depth == 0 or _winner(board) is not None:
            return _utility(board, depth_limit - depth)

        if maximizing:
            children = _children(board, "X", rng)
            nodes_expanded += 1
            nodes_generated += len(children)
            values = [expected_value(child, depth - 1, False) for _action, child in children]
            return max(values) if values else _utility(board, depth_limit - depth)

        children = _children(board, "O", rng)
        nodes_expanded += 1
        nodes_generated += len(children)
        if not children:
            return _utility(board, depth_limit - depth)
        probability = 1.0 / len(children)
        return sum(
            probability * expected_value(child, depth - 1, True)
            for _action, child in children
        )

    def choose_max_move(board):
        scored = []
        for action, child in _children(board, "X", rng):
            chance_children = _children(child, "O", rng)
            if not chance_children:
                score = _utility(child, 1)
                outcomes = [child]
            else:
                probability = 1.0 / len(chance_children)
                score = sum(
                    probability * expected_value(outcome, depth_limit - 1, True)
                    for _chance_action, outcome in chance_children
                )
                outcomes = [outcome for _chance_action, outcome in chance_children]
            scored.append((score, action, child, outcomes))

        if not scored:
            return _utility(board, 0), None, board, []
        return max(scored, key=lambda item: (item[0], item[1]))

    board = CARO_START
    actions = []
    step_boards = []
    final_score = _utility(board, 0)
    chance_outcomes = []
    max_frontier_size = 1

    while _winner(board) is None:
        score, action, next_board, outcomes = choose_max_move(board)
        if action is None:
            break
        actions.append(action)
        board = next_board
        step_boards.append(board)
        final_score = score
        chance_outcomes = outcomes
        max_frontier_size = max(max_frontier_size, len(outcomes), len(_moves(board)))
        if _winner(board) is not None:
            break

        chance_children = _children(board, "O", rng)
        nodes_expanded += 1
        nodes_generated += len(chance_children)
        if not chance_children:
            break
        chance_action, board = rng.choice(chance_children)
        actions.append(chance_action)
        step_boards.append(board)
        max_frontier_size = max(max_frontier_size, len(chance_children), len(_moves(board)))

    winner = _winner(board)

    runtime_ms = (time.perf_counter() - start_time) * 1000
    details = [
        "Demo Caro 3x3: MAX=X, Chance=O replies.",
        f"Start: {_board_text(CARO_START)}",
        f"Moves: {' -> '.join(actions) if actions else 'No move'}",
        f"Final: {_board_text(board)}",
        f"Result: {_winner_text(winner)}; moves: {len(actions)}.",
        f"Expected utility: {final_score:.2f}; last chance outcomes: {len(chance_outcomes)}.",
        f"Expanded: {nodes_expanded}; generated: {nodes_generated}.",
    ]

    return _demo_result(
        algorithm="Expectimax",
        actions=actions,
        step_boards=step_boards,
        final_score=final_score,
        final_board=board,
        winner=winner,
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        max_frontier_size=max_frontier_size,
        runtime_ms=runtime_ms,
        details=details,
        summary_lines=[
            f"Kết quả: {_winner_text(winner)}",
            f"Số nước: {len(actions)}",
            f"Chance cuối: {len(chance_outcomes)} | Node: {nodes_expanded}/{nodes_generated}",
        ],
    )


minimax = minimax_search
alpha_beta = alpha_beta_search
expectimax = expectimax_search
