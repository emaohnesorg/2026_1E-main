from __future__ import annotations
from typing import Any

# =========================
# ROTATION
# =========================
def rotate(m):
    return [list(row) for row in zip(*m[::-1])]


# =========================
# BOARD HELPERS
# =========================
def clear_lines(board):
    new_board = [row for row in board if not all(row)]
    while len(new_board) < 20:
        new_board.insert(0, [0] * 10)
    return new_board


def drop(board, matrix, x):
    y = 0

    while True:
        collision = False

        for py in range(len(matrix)):
            for px in range(len(matrix[py])):
                if not matrix[py][px]:
                    continue

                bx = x + px
                by = y + py + 1

                if by >= 20:
                    collision = True
                    break

                if by >= 0 and board[by][bx]:
                    collision = True
                    break

        if collision:
            break

        y += 1

    return y


def place(board, matrix, x, y):
    b = [row[:] for row in board]

    for py in range(len(matrix)):
        for px in range(len(matrix[py])):
            if matrix[py][px]:
                by = y + py
                bx = x + px
                if 0 <= by < 20:
                    b[by][bx] = 1
    return b


# =========================
# HEURISTIC
# =========================
def evaluate(board):
    heights = [0] * 10
    holes = 0
    bumpiness = 0
    full_lines = 0

    # heights + holes
    for x in range(10):
        seen = False
        col_height = 0

        for y in range(20):
            if board[y][x]:
                if not seen:
                    col_height = 20 - y
                    seen = True
            else:
                if seen:
                    holes += 1

        heights[x] = col_height

    # bumpiness
    for x in range(9):
        bumpiness += abs(heights[x] - heights[x + 1])

    # lines
    for y in range(20):
        if all(board[y]):
            full_lines += 1

    return (
        sum(heights) * 0.5 +
        holes * 12 +
        bumpiness * 0.3 -
        full_lines * 100
    )


# =========================
# SEARCH
# =========================
def search(board, piece):
    base = piece["matrix"]

    best_score = float("inf")
    best_move = (0, 0)

    for r in range(4):
        m = base
        for _ in range(r):
            m = rotate(m)

        width = len(m[0])

        for x in range(10 - width + 1):
            # simulate drop + validity
            y = 0
            while True:
                collision = False
                for py in range(len(m)):
                    for px in range(len(m[py])):
                        if not m[py][px]:
                            continue

                        bx = x + px
                        by = y + py

                        if by >= 20:
                            collision = True
                            break

                        if by >= 0 and board[by][bx]:
                            collision = True
                            break
                    if collision:
                        break

                if collision:
                    break

                y += 1

            y -= 1

            if y < 0:
                continue

            # place
            b = place(board, m, x, y)
            b = clear_lines(b)

            score = evaluate(b)

            if score < best_score:
                best_score = score
                best_move = (r, x)

    return best_move


# =========================
# BOT STATE
# =========================
current_piece_type = None
plan = []


# =========================
# MAIN
# =========================
def choose_command(snapshot: dict[str, Any]) -> str:
    global current_piece_type, plan

    piece = snapshot["currentPiece"]
    board = snapshot["board"]
    if piece["type"] != current_piece_type:
        current_piece_type = piece["type"]

        r, target_x = search(board, piece)

        plan = []
        plan += ["rotate"] * r
        # stabilizace rotace (důležité!)
        plan += ["down"] * 2

        dx = target_x - piece["x"]
        if dx > 0:
            plan += ["right"] * dx
        elif dx < 0:
            plan += ["left"] * (-dx)

        plan += ["drop"]

    if not plan:
        return "drop"

    return plan.pop(0)