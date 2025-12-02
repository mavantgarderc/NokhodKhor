from typing import List, Tuple

import pygame

from config import HEIGHT, WIDTH


def draw_player(
    screen: pygame.Surface,
    player_images,
    counter: int,
    player_x: float,
    player_y: float,
    direction: int,
) -> None:
    """Draw the player sprite with the correct orientation and animation frame."""
    frame = counter // 5
    img = player_images[frame]

    if direction == 0:
        screen.blit(img, (player_x, player_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(img, True, False), (player_x, player_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(img, 90), (player_x, player_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(img, 270), (player_x, player_y))


def check_position(
    centerx: float,
    centery: float,
    direction: int,
    level: List[List[int]],
) -> List[bool]:
    """Return allowed turns [R, L, U, D] for the player at given center position."""
    turns = [False, False, False, False]
    num1 = (HEIGHT - 50) // 32
    num2 = WIDTH // 30
    num3 = 15

    if centerx // 30 < 29:
        if direction == 0:
            if level[centery // num1][(centerx - num3) // num2] < 3:
                turns[1] = True
        if direction == 1:
            if level[centery // num1][(centerx + num3) // num2] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery + num3) // num1][centerx // num2] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery - num3) // num1][centerx // num2] < 3:
                turns[2] = True

        if direction == 2 or direction == 3:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num2) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num2) // num2] < 3:
                    turns[0] = True

        if direction == 0 or direction == 1:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num1) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num1) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True
    else:
        turns[0] = True
        turns[1] = True

    return turns


def move_player(
    play_x: float,
    play_y: float,
    direction: int,
    turns_allowed: List[bool],
    player_speed: float,
) -> Tuple[float, float]:
    """Move the player according to current direction and allowed turns."""
    # r, l, u, d
    if direction == 0 and turns_allowed[0]:
        play_x += player_speed
    elif direction == 1 and turns_allowed[1]:
        play_x -= player_speed
    if direction == 2 and turns_allowed[2]:
        play_y -= player_speed
    elif direction == 3 and turns_allowed[3]:
        play_y += player_speed
    return play_x, play_y


def check_collisions(
    score: int,
    power: bool,
    power_count: int,
    eaten_ghosts: List[bool],
    player_x: float,
    center_x: float,
    center_y: float,
    level: List[List[int]],
) -> Tuple[int, bool, int, List[bool]]:
    """Handle pellet / power-pellet collisions and scoring."""
    num1 = (HEIGHT - 50) // 32
    num2 = WIDTH // 30

    if 0 < player_x < 870:
        row = center_y // num1
        col = center_x // num2
        if level[row][col] == 1:
            level[row][col] = 0
            score += 10
        if level[row][col] == 2:
            level[row][col] = 0
            score += 50
            power = True
            power_count = 0
            eaten_ghosts = [False, False, False, False]

    return score, power, power_count, eaten_ghosts
