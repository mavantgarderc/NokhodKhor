import copy

from nokhodkhor.board import BASE_LEVEL
from nokhodkhor.config import HEIGHT, WIDTH
from nokhodkhor.player import check_collisions, check_position


def _tile_center(i: int, j: int):
    num1 = (HEIGHT - 50) // 32
    num2 = WIDTH // 30
    center_x = j * num2 + 0.5 * num2
    center_y = i * num1 + 0.5 * num1
    return center_x, center_y


def test_check_position_horizontal_corridor():
    level = copy.deepcopy(BASE_LEVEL)
    i, j = 24, 15
    center_x, center_y = _tile_center(i, j)

    direction = 0
    turns = check_position(center_x, center_y, direction, level)

    assert turns[0] is True
    assert turns[1] is True
    assert turns[2] is False
    assert turns[3] is False


def test_check_collisions_regular_pellet():

    level = copy.deepcopy(BASE_LEVEL)

    pellet_pos = None
    for i, row in enumerate(level):
        for j, val in enumerate(row):
            if val == 1:
                pellet_pos = (i, j)
                break
        if pellet_pos:
            break

    assert pellet_pos is not None, "No pellet (1) found in base level?"

    i, j = pellet_pos
    center_x, center_y = _tile_center(i, j)

    score = 0
    power = False
    power_count = 123
    eaten_ghosts = [True, True, True, True]
    player_x = 100

    score2, power2, power_count2, eaten2 = check_collisions(
        score, power, power_count, eaten_ghosts, player_x, center_x, center_y, level
    )

    assert score2 == score + 10
    assert power2 is False
    assert power_count2 == power_count
    assert eaten2 == eaten_ghosts
    assert level[i][j] == 0


def test_check_collisions_power_pellet():

    level = copy.deepcopy(BASE_LEVEL)

    power_pos = None
    for i, row in enumerate(level):
        for j, val in enumerate(row):
            if val == 2:
                power_pos = (i, j)
                break
        if power_pos:
            break

    assert power_pos is not None, "No power pellet (2) found in base level?"

    i, j = power_pos
    center_x, center_y = _tile_center(i, j)

    score = 0
    power = False
    power_count = 999
    eaten_ghosts = [True, True, True, True]
    player_x = 100

    score2, power2, power_count2, eaten2 = check_collisions(
        score, power, power_count, eaten_ghosts, player_x, center_x, center_y, level
    )

    assert score2 == score + 50
    assert power2 is True
    assert power_count2 == 0
    assert eaten2 == [False, False, False, False]
    assert level[i][j] == 0
