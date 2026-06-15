from __future__ import annotations

from typing import Any

TARGET_COLUMNS = {
    "I": 4,
    "J": 1,
    "L": 8,
    "O": 5,
    "S": 3,
    "T": 6,
    "Z": 7,
}


import random
def choose_command(snapshot):
    return random.choice(["left", "right", "rotate", "down"])