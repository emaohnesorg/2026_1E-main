from __future__ import annotations

from typing import Any

target_column = None
current_piece_type = None


def get_column_heights(board):
    heights = []

    for x in range(10):
        height = 0

        for y in range(20):
            cell = board[y][x]

            if cell and not str(cell).endswith("_active"):
                height = 20 - y
                break

        heights.append(height)

    return heights


def choose_best_column(board):
    heights = get_column_heights(board)

    best = 0

    for i in range(1, 10):
        if heights[i] < heights[best]:
            best = i

    return best


def choose_command(snapshot: dict[str, Any]) -> str:
    global target_column
    global current_piece_type

    piece = snapshot["currentPiece"]
    board = snapshot["board"]

    # nová kostka
    if piece["type"] != current_piece_type:
        current_piece_type = piece["type"]
        target_column = choose_best_column(board)

    x = piece["x"]

    if x < target_column:
        return "right"

    if x > target_column:
        return "left"

    return "drop"