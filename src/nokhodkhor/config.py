import math

import pygame

WIDTH = 900
HEIGHT = 950
FPS = 60


FONT_NAME = "freesansbold.ttf"
FONT_SIZE = 20


PLAYER_START_X = 450
PLAYER_START_Y = 663


BLINKY_START = (56, 58, 0)
INKY_START = (440, 388, 2)
PINKY_START = (440, 438, 2)
CLYDE_START = (440, 438, 2)


COLOR_BG = "black"
COLOR_WALL = "purple"
COLOR_TEXT = "white"


STARTUP_DELAY_FRAMES = 180


PI = math.pi


DIFFICULTIES = {
    "easy": {
        "player_speed": 2.2,
        "ghost_speed": 1.7,
        "frightened_speed": 1.2,
        "eaten_speed": 4.0,
        "powerup_duration": 900,
        "lives": 5,
    },
    "normal": {
        "player_speed": 2.0,
        "ghost_speed": 2.0,
        "frightened_speed": 1.0,
        "eaten_speed": 4.0,
        "powerup_duration": 600,
        "lives": 3,
    },
    "hard": {
        "player_speed": 2.0,
        "ghost_speed": 2.4,
        "frightened_speed": 1.2,
        "eaten_speed": 5.0,
        "powerup_duration": 400,
        "lives": 2,
    },
}

DEFAULT_DIFFICULTY = "normal"


DEFAULT_KEY_BINDINGS = {
    "move_right": pygame.K_RIGHT,
    "move_left": pygame.K_LEFT,
    "move_up": pygame.K_UP,
    "move_down": pygame.K_DOWN,
    "pause": pygame.K_p,
    "restart": pygame.K_SPACE,
}


ACTION_LABELS = {
    "move_right": "Move Right",
    "move_left": "Move Left",
    "move_up": "Move Up",
    "move_down": "Move Down",
    "pause": "Pause / Resume",
    "restart": "Restart",
}


ACTION_ORDER = [
    "move_right",
    "move_left",
    "move_up",
    "move_down",
    "pause",
    "restart",
]
