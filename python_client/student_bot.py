from __future__ import annotations
from typing import Any


def rotate(m):
    return [list(row) for row in zip(*m[::-1])]


def clear_lines(board):
    new_board = [row[:] for row in board if not all(row)]

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

                if board[by][bx]:
                    collision = True
                    break

            if collision:
                break

        if collision:
            return y

        y += 1


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


def evaluate(board):
    heights = [0] * 10
    holes = 0
    bumpiness = 0

    for x in range(10):
        found_block = False

        for y in range(20):
            if board[y][x]:
                if not found_block:
                    heights[x] = 20 - y
                    found_block = True
            else:
                if found_block:
                    holes += 1

    for x in range(9):
        bumpiness += abs(heights[x] - heights[x + 1])

    max_height = max(heights)

    flatness = 0
    avg = sum(heights) / 10

    for h in heights:
        flatness -= abs(h - avg)

    return (
        holes * 120 +
        sum(heights) * 0.4 +
        bumpiness * 0.8 +
        max_height * 25 +
        flatness * 0.2
    )


def search(board, piece):
    best_score = float("inf")
    best_move = (0, piece["x"])

    base = piece["matrix"]

    for rotations in range(4):

        matrix = base

        for _ in range(rotations):
            matrix = rotate(matrix)

        width = len(matrix[0])

        for x in range(10 - width + 1):

            y = drop(board, matrix, x)

            simulated = place(board, matrix, x, y)

            lines = 0
            for row in simulated:
                if all(row):
                    lines += 1

            simulated = clear_lines(simulated)

            score = evaluate(simulated)

            score -= lines * 10000

            if score < best_score:
                best_score = score
                best_move = (rotations, x)

    return best_move


plan = []

last_spawn_signature = None


def choose_command(snapshot: dict[str, Any]) -> str:
    global plan
    global last_spawn_signature

    piece = snapshot["currentPiece"]
    board = snapshot["board"]

    spawn_signature = (
        piece["type"],
        piece["x"],
        piece["y"]
    )

    if piece["y"] <= 1 and spawn_signature != last_spawn_signature:

        last_spawn_signature = spawn_signature

        rotations, target_x = search(board, piece)

        plan = []

        for _ in range(rotations):
            plan.append("rotate")

        dx = target_x - piece["x"]

        if dx > 0:
            plan += ["right"] * dx
        elif dx < 0:
            plan += ["left"] * (-dx)

        plan.append("drop")

    if plan:
        return plan.pop(0)

    return "down"