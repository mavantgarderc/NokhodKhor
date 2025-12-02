import copy

from nokhodkhor.board import BASE_LEVEL, boards


def test_board_dimensions():
    rows = len(BASE_LEVEL)
    assert rows > 0
    cols = len(BASE_LEVEL[0])
    assert cols == 30

    assert all(len(row) == cols for row in BASE_LEVEL)

    assert len(boards) >= 1
    for level in boards:
        assert len(level) == rows
        assert all(len(row) == cols for row in level)


def test_walls_and_gates_unchanged_across_levels():

    for lvl in boards:
        for i, row in enumerate(BASE_LEVEL):
            for j, val in enumerate(row):
                if val not in (0, 1, 2):
                    assert lvl[i][j] == val


def test_first_level_equals_base_layout():

    assert boards[0] == BASE_LEVEL
