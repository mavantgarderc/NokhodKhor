import copy
import random

import pygame

from .board import boards, draw_board
from .config import (
    ACTION_LABELS,
    ACTION_ORDER,
    BLINKY_START,
    CLYDE_START,
    COLOR_BG,
    DEFAULT_DIFFICULTY,
    DEFAULT_KEY_BINDINGS,
    DEFAULT_KEY_BINDINGS_P2,
    DEFAULT_MULTIPLAYER_MODE,
    DEFAULT_THEME_MODE,
    DIFFICULTIES,
    FONT_NAME,
    FONT_SIZE,
    FPS,
    HEIGHT,
    INKY_START,
    MULTIPLAYER_MODES,
    PINKY_START,
    PLAYER2_START_X,
    PLAYER2_START_Y,
    PLAYER_START_X,
    PLAYER_START_Y,
    STARTUP_DELAY_FRAMES,
    THEME_MODES,
    THEME_RULES,
    WIDTH,
)
from .ghosts import Ghost
from .hud import draw_misc
from .player import check_collisions, check_position, draw_player, move_player
from .scores import get_high_score, load_high_scores, maybe_update_high_score, save_high_scores


def run() -> None:
    pygame.init()
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    timer = pygame.time.Clock()
    font = pygame.font.Font(FONT_NAME, FONT_SIZE)

    player_images = []
    for i in range(1, 5):
        player_images.append(
            pygame.transform.scale(pygame.image.load(f"assets/player_images/{i}.png"), (40, 40))
        )
    blinky_img = pygame.transform.scale(pygame.image.load("assets/ghost_images/red.png"), (42, 42))
    pinky_img = pygame.transform.scale(pygame.image.load("assets/ghost_images/pink.png"), (42, 42))
    inky_img = pygame.transform.scale(pygame.image.load("assets/ghost_images/blue.png"), (42, 42))
    clyde_img = pygame.transform.scale(pygame.image.load("assets/ghost_images/orange.png"), (42, 42))
    spooked_img = pygame.transform.scale(pygame.image.load("assets/ghost_images/powerup.png"), (42, 42))
    dead_img = pygame.transform.scale(pygame.image.load("assets/ghost_images/dead.png"), (42, 42))

    difficulty_name = DEFAULT_DIFFICULTY
    difficulty = DIFFICULTIES[difficulty_name]

    theme_mode = DEFAULT_THEME_MODE
    theme_rules = THEME_RULES[theme_mode]

    player_speed = difficulty["player_speed"]
    powerup_duration_frames = int(
        difficulty["powerup_duration"] * theme_rules["powerup_duration_multiplier"]
    )
    max_lives = max(1, int(difficulty["lives"] * theme_rules["lives_multiplier"]))

    key_bindings = DEFAULT_KEY_BINDINGS.copy()
    key_bindings_p2 = DEFAULT_KEY_BINDINGS_P2.copy()

    high_scores = load_high_scores()
    current_high_score = get_high_score(high_scores, difficulty_name)
    run_recorded = False

    multiplayer_mode = DEFAULT_MULTIPLAYER_MODE
    multiplayer_menu_index = MULTIPLAYER_MODES.index(multiplayer_mode)
    versus_ghost_index = 0

    PAUSE_MENU_ITEMS = [
        "Resume",
        "Restart",
        "Change Difficulty",
        "Theme Mode",
        "Multiplayer",
        "Quit",
    ]
    pause_menu_index = 0

    remap_mode = False
    remap_order: list[str] = []
    remap_index = 0
    remap_prompt: str | None = None

    show_help = False

    current_level_index = 0
    total_levels = len(boards)
    level = copy.deepcopy(boards[current_level_index])

    player_x = PLAYER_START_X
    player_y = PLAYER_START_Y
    direction = 0
    direction_command = 0
    score = 0

    player2_x = PLAYER2_START_X
    player2_y = PLAYER2_START_Y
    direction2 = 0
    direction2_command = 0
    score2 = 0

    blinky_x, blinky_y, blinky_direction = BLINKY_START
    inky_x, inky_y, inky_direction = INKY_START
    pinky_x, pinky_y, pinky_direction = PINKY_START
    clyde_x, clyde_y, clyde_direction = CLYDE_START

    blinky_dead = False
    inky_dead = False
    clyde_dead = False
    pinky_dead = False

    ghost_player_direction = 0
    ghost_player_direction_command = 0

    counter = 0
    flicker = False
    turns_allowed = [False, False, False, False]
    turns_allowed2 = [False, False, False, False]

    powerup = False
    power_counter = 0
    eaten_ghost = [False, False, False, False]
    targets = [
        (player_x, player_y),
        (player_x, player_y),
        (player_x, player_y),
        (player_x, player_y),
    ]

    ghost_speeds = [2, 2, 2, 2]
    startup_counter = 0
    lives = max_lives
    game_over = False
    game_won = False
    moving = False
    paused = False

    chaos_timer = 0
    CHAOS_INTERVAL_FRAMES = 5 * FPS

    running = True

    def apply_difficulty(name: str) -> None:
        nonlocal difficulty_name, difficulty
        nonlocal player_speed, powerup_duration_frames, max_lives
        nonlocal current_high_score, theme_rules

        difficulty_name = name
        difficulty = DIFFICULTIES[difficulty_name]

        player_speed = difficulty["player_speed"]
        powerup_duration_frames = int(
            difficulty["powerup_duration"] * theme_rules["powerup_duration_multiplier"]
        )
        max_lives = max(1, int(difficulty["lives"] * theme_rules["lives_multiplier"]))

        current_high_score = get_high_score(high_scores, difficulty_name)

    def soft_reset() -> None:
        nonlocal player_x, player_y, direction, direction_command
        nonlocal player2_x, player2_y, direction2, direction2_command
        nonlocal blinky_x, blinky_y, blinky_direction
        nonlocal inky_x, inky_y, inky_direction
        nonlocal pinky_x, pinky_y, pinky_direction
        nonlocal clyde_x, clyde_y, clyde_direction
        nonlocal eaten_ghost, blinky_dead, inky_dead, pinky_dead, clyde_dead
        nonlocal powerup, power_counter, startup_counter
        nonlocal paused, remap_mode, remap_prompt, run_recorded, pause_menu_index
        nonlocal show_help

        powerup = False
        power_counter = 0
        startup_counter = 0
        paused = False
        remap_mode = False
        remap_prompt = None
        show_help = False
        run_recorded = False
        pause_menu_index = 0

        player_x, player_y = PLAYER_START_X, PLAYER_START_Y
        direction = 0
        direction_command = 0

        player2_x, player2_y = PLAYER2_START_X, PLAYER2_START_Y
        direction2 = 0
        direction2_command = 0

        blinky_x, blinky_y, blinky_direction = BLINKY_START
        inky_x, inky_y, inky_direction = INKY_START
        pinky_x, pinky_y, pinky_direction = PINKY_START
        clyde_x, clyde_y, clyde_direction = CLYDE_START

        eaten_ghost = [False, False, False, False]
        blinky_dead = False
        inky_dead = False
        pinky_dead = False
        clyde_dead = False

    def respawn_player(player_idx: int) -> None:
        nonlocal player_x, player_y, direction, direction_command
        nonlocal player2_x, player2_y, direction2, direction2_command

        if player_idx == 1:
            player_x, player_y = PLAYER_START_X, PLAYER_START_Y
            direction = 0
            direction_command = 0
        elif player_idx == 2:
            player2_x, player2_y = PLAYER2_START_X, PLAYER2_START_Y
            direction2 = 0
            direction2_command = 0

    def load_level(idx: int) -> None:
        nonlocal level, current_level_index
        current_level_index = idx
        level = copy.deepcopy(boards[current_level_index])
        soft_reset()

    def full_restart() -> None:
        nonlocal score, score2, lives, level, game_over, game_won, run_recorded
        score = 0
        score2 = 0
        lives = max_lives
        run_recorded = False
        load_level(0)
        game_over = False
        game_won = False

    def start_remap_mode() -> None:
        nonlocal remap_mode, remap_order, remap_index, remap_prompt, paused, show_help
        remap_mode = True
        paused = True
        show_help = False
        remap_order = ACTION_ORDER.copy()
        remap_index = 0
        remap_prompt = ACTION_LABELS[remap_order[remap_index]]

    def handle_remap_key(key: int) -> None:
        nonlocal remap_mode, remap_index, remap_prompt, paused

        if key == pygame.K_ESCAPE:
            remap_mode = False
            remap_prompt = None
            paused = False
            return

        action = remap_order[remap_index]
        key_bindings[action] = key
        remap_index += 1
        if remap_index >= len(remap_order):
            remap_mode = False
            remap_prompt = None
            paused = False
        else:
            remap_prompt = ACTION_LABELS[remap_order[remap_index]]

    def finalize_run_if_needed() -> None:
        nonlocal run_recorded, current_high_score, theme_rules
        if (game_over or game_won) and not run_recorded:
            if theme_rules.get("record_high_scores", True):
                if maybe_update_high_score(high_scores, difficulty_name, score):
                    save_high_scores(high_scores)
                current_high_score = get_high_score(high_scores, difficulty_name)
            run_recorded = True

    def build_bindings_display() -> list[tuple[str, str]]:
        pairs: list[tuple[str, str]] = []
        for action in ACTION_ORDER:
            key_code = key_bindings[action]
            key_name = pygame.key.name(key_code)
            label = ACTION_LABELS[action]
            pairs.append((label, key_name))
        return pairs

    def cycle_multiplayer_mode() -> None:
        nonlocal multiplayer_mode, multiplayer_menu_index
        nonlocal versus_ghost_index, ghost_player_direction, ghost_player_direction_command
        nonlocal player2_x, player2_y, direction2, direction2_command

        idx = MULTIPLAYER_MODES.index(multiplayer_mode)
        multiplayer_mode = MULTIPLAYER_MODES[(idx + 1) % len(MULTIPLAYER_MODES)]
        multiplayer_menu_index = MULTIPLAYER_MODES.index(multiplayer_mode)

        if multiplayer_mode == "Co-op":
            player2_x, player2_y = PLAYER2_START_X, PLAYER2_START_Y
            direction2 = 0
            direction2_command = 0
        elif multiplayer_mode == "Versus":
            versus_ghost_index = 0
            ghost_player_direction = 0
            ghost_player_direction_command = 0

    def cycle_theme_mode() -> None:
        nonlocal theme_mode, theme_rules
        nonlocal player_speed, powerup_duration_frames, max_lives
        nonlocal difficulty, chaos_timer

        idx = THEME_MODES.index(theme_mode)
        theme_mode = THEME_MODES[(idx + 1) % len(THEME_MODES)]
        theme_rules = THEME_RULES[theme_mode]

        chaos_timer = 0

        player_speed = difficulty["player_speed"]
        powerup_duration_frames = int(
            difficulty["powerup_duration"] * theme_rules["powerup_duration_multiplier"]
        )
        max_lives = max(1, int(difficulty["lives"] * theme_rules["lives_multiplier"]))

    def ghost_is_player_controlled(ghost_id: int) -> bool:
        return multiplayer_mode == "Versus" and ghost_id == versus_ghost_index

    while running:
        timer.tick(FPS)

        if not paused and not remap_mode and not show_help:
            if counter < 19:
                counter += 1
                if counter > 3:
                    flicker = False
            else:
                counter = 0
                flicker = True

            if powerup and power_counter < powerup_duration_frames:
                power_counter += 1
            elif powerup and power_counter >= powerup_duration_frames:
                power_counter = 0
                powerup = False
                eaten_ghost = [False, False, False, False]

            if startup_counter < STARTUP_DELAY_FRAMES and not game_over and not game_won:
                moving = False
                startup_counter += 1
            else:
                moving = True

        if (
            theme_mode == "chaos"
            and not paused
            and not remap_mode
            and not show_help
            and not game_over
            and not game_won
        ):
            chaos_timer += 1
            if chaos_timer >= CHAOS_INTERVAL_FRAMES:
                chaos_timer = 0

                random_mult = random.uniform(0.8, 1.3)
                theme_rules = {
                    **theme_rules,
                    "ghost_speed_multiplier": random_mult,
                }

        screen.fill(COLOR_BG)
        draw_board(screen, level, flicker)

        center_x = player_x + 23
        center_y = player_y + 24
        center2_x = player2_x + 23
        center2_y = player2_y + 24

        if powerup:
            base_speed = difficulty["frightened_speed"]
        else:
            base_speed = difficulty["ghost_speed"]

        base_speed *= theme_rules["ghost_speed_multiplier"]
        ghost_speeds = [base_speed] * 4

        for idx in range(4):
            if eaten_ghost[idx]:
                ghost_speeds[idx] = difficulty["ghost_speed"] * theme_rules["ghost_speed_multiplier"]

        if blinky_dead:
            ghost_speeds[0] = difficulty["eaten_speed"] * theme_rules["ghost_speed_multiplier"]
        if inky_dead:
            ghost_speeds[1] = difficulty["eaten_speed"] * theme_rules["ghost_speed_multiplier"]
        if pinky_dead:
            ghost_speeds[2] = difficulty["eaten_speed"] * theme_rules["ghost_speed_multiplier"]
        if clyde_dead:
            ghost_speeds[3] = difficulty["eaten_speed"] * theme_rules["ghost_speed_multiplier"]

        level_cleared = True
        for row in level:
            if 1 in row or 2 in row:
                level_cleared = False
                break

        if level_cleared and not game_over and not game_won:
            if current_level_index + 1 < total_levels:
                load_level(current_level_index + 1)
                pygame.display.flip()
                continue
            else:
                game_won = True
                moving = False

        player_circle = pygame.draw.circle(screen, "black", (center_x, center_y), 20, 2)
        draw_player(screen, player_images, counter, player_x, player_y, direction)
        if multiplayer_mode != "1P":
            label1 = font.render("1", True, "white")
            screen.blit(label1, (center_x - 5, center_y - 10))

        player2_circle = None
        if multiplayer_mode == "Co-op":
            player2_circle = pygame.draw.circle(screen, "black", (center2_x, center2_y), 20, 2)
            draw_player(screen, player_images, counter, player2_x, player2_y, direction2)
            label2 = font.render("2", True, "white")
            screen.blit(label2, (center2_x - 5, center2_y - 10))

        blinky = Ghost(
            blinky_x,
            blinky_y,
            targets[0],
            ghost_speeds[0],
            blinky_img,
            blinky_direction,
            blinky_dead,
            0,
        )
        inky = Ghost(
            inky_x,
            inky_y,
            targets[1],
            ghost_speeds[1],
            inky_img,
            inky_direction,
            inky_dead,
            1,
        )
        pinky = Ghost(
            pinky_x,
            pinky_y,
            targets[2],
            ghost_speeds[2],
            pinky_img,
            pinky_direction,
            pinky_dead,
            2,
        )
        clyde = Ghost(
            clyde_x,
            clyde_y,
            targets[3],
            ghost_speeds[3],
            clyde_img,
            clyde_direction,
            clyde_dead,
            3,
        )

        for ghost in (blinky, inky, pinky, clyde):
            ghost.update_collision_state(level)
            ghost.draw(screen, powerup, eaten_ghost, spooked_img, dead_img)

        bindings_display = build_bindings_display()
        draw_misc(
            screen,
            font,
            score,
            score2,
            current_high_score,
            powerup,
            lives,
            game_over,
            game_won,
            player_images,
            paused,
            pause_menu_index,
            difficulty_name,
            theme_mode,
            current_level_index,
            total_levels,
            show_help,
            bindings_display,
            remap_prompt,
            multiplayer_mode,
            versus_ghost_index,
        )

        def get_targets(
            blink_x,
            blink_y,
            ink_x,
            ink_y,
            pink_x,
            pink_y,
            clyd_x,
            clyd_y,
        ):
            nonlocal powerup, eaten_ghost, player_x, player_y, player2_x, player2_y
            nonlocal multiplayer_mode, direction, direction2

            def nearest_player(gx: float, gy: float) -> tuple[float, float, int]:
                gx_c = gx + 22
                gy_c = gy + 22

                p1_cx = player_x + 23
                p1_cy = player_y + 24
                best_x, best_y, best_dir = player_x, player_y, direction
                best_d = (gx_c - p1_cx) ** 2 + (gy_c - p1_cy) ** 2

                if multiplayer_mode == "Co-op":
                    p2_cx = player2_x + 23
                    p2_cy = player2_y + 24
                    d2 = (gx_c - p2_cx) ** 2 + (gy_c - p2_cy) ** 2
                    if d2 < best_d:
                        best_d = d2
                        best_x, best_y, best_dir = player2_x, player2_y, direction2

                return best_x, best_y, best_dir

            def runaway_for(px: float, py: float) -> tuple[int, int]:
                if px < 450:
                    rx = 900
                else:
                    rx = 0
                if py < 450:
                    ry = 900
                else:
                    ry = 0
                return rx, ry

            return_target = (380, 400)

            def dir_vector(dir_code: int) -> tuple[int, int]:
                dx, dy = 0, 0
                if dir_code == 0:
                    dx = 1
                elif dir_code == 1:
                    dx = -1
                elif dir_code == 2:
                    dy = -1
                elif dir_code == 3:
                    dy = 1
                return dx, dy

            num1 = (HEIGHT - 50) // 32
            num2 = WIDTH // 30

            def ahead_pixel(px: float, py: float, dir_code: int, tiles_ahead: int) -> tuple[float, float]:
                dx, dy = dir_vector(dir_code)
                return (
                    px + dx * tiles_ahead * num2,
                    py + dy * tiles_ahead * num1,
                )

            blink_px, blink_py, blink_dir = nearest_player(blink_x, blink_y)
            blinky_chase = (blink_px, blink_py)

            ink_px, ink_py, ink_dir = nearest_player(ink_x, ink_y)
            inky_target_px, inky_target_py = ahead_pixel(ink_px, ink_py, ink_dir, 2)

            pink_px, pink_py, pink_dir = nearest_player(pink_x, pink_y)
            pinky_target_px, pinky_target_py = ahead_pixel(pink_px, pink_py, pink_dir, 4)

            clyd_px, clyd_py, _ = nearest_player(clyd_x, clyd_y)
            clyde_offset_px = clyd_px + 0.5 * num2
            clyde_offset_py = clyd_py + 0.5 * num1

            blink_runx, blink_runy = runaway_for(blink_px, blink_py)
            ink_runx, ink_runy = runaway_for(ink_px, ink_py)
            pink_runx, pink_runy = runaway_for(pink_px, pink_py)
            clyd_runx, clyd_runy = runaway_for(clyd_px, clyd_py)

            if powerup:
                if not blinky.dead and not eaten_ghost[0]:
                    blink_target = (blink_runx, blink_runy)
                elif not blinky.dead and eaten_ghost[0]:
                    if 340 < blink_x < 560 and 340 < blink_y < 500:
                        blink_target = (400, 100)
                    else:
                        blink_target = blinky_chase
                else:
                    blink_target = return_target

                if not inky.dead and not eaten_ghost[1]:
                    ink_target = (ink_runx, ink_py)
                elif not inky.dead and eaten_ghost[1]:
                    if 340 < ink_x < 560 and 340 < ink_y < 500:
                        ink_target = (400, 100)
                    else:
                        ink_target = (inky_target_px, inky_target_py)
                else:
                    ink_target = return_target

                if not pinky.dead and not eaten_ghost[2]:
                    pink_target = (pink_px, pink_runy)
                elif not pinky.dead and eaten_ghost[2]:
                    if 340 < pink_x < 560 and 340 < pink_y < 500:
                        pink_target = (400, 100)
                    else:
                        pink_target = (pinky_target_px, pinky_target_py)
                else:
                    pink_target = return_target

                if not clyde.dead and not eaten_ghost[3]:
                    clyd_target = (clyd_runx, clyd_runy)
                elif not clyde.dead and eaten_ghost[3]:
                    if 340 < clyd_x < 560 and 340 < clyd_y < 500:
                        clyd_target = (400, 100)
                    else:
                        clyd_target = (clyde_offset_px, clyde_offset_py)
                else:
                    clyd_target = return_target
            else:
                if not blinky.dead:
                    if 340 < blink_x < 560 and 340 < blink_y < 500:
                        blink_target = (400, 100)
                    else:
                        blink_target = blinky_chase
                else:
                    blink_target = return_target

                if not inky.dead:
                    if 340 < ink_x < 560 and 340 < ink_y < 500:
                        ink_target = (400, 100)
                    else:
                        ink_target = (inky_target_px, inky_target_py)
                else:
                    ink_target = return_target

                if not pinky.dead:
                    if 340 < pink_x < 560 and 340 < pink_y < 500:
                        pink_target = (400, 100)
                    else:
                        pink_target = (pinky_target_px, pinky_target_py)
                else:
                    pink_target = return_target

                if not clyde.dead:
                    if 340 < clyd_x < 560 and 340 < clyd_y < 500:
                        clyd_target = (400, 100)
                    else:
                        clyd_target = (clyde_offset_px, clyde_offset_py)
                else:
                    clyd_target = return_target

            return [blink_target, ink_target, pink_target, clyd_target]

        targets = get_targets(blinky_x, blinky_y, inky_x, inky_y, pinky_x, pinky_y, clyde_x, clyde_y)

        can_update_positions = (
            moving and not paused and not remap_mode and not show_help and not game_over and not game_won
        )

        if can_update_positions:
            turns_allowed = check_position(center_x, center_y, direction, level)
            player_x, player_y = move_player(player_x, player_y, direction, turns_allowed, player_speed)

            if multiplayer_mode == "Co-op":
                turns_allowed2 = check_position(center2_x, center2_y, direction2, level)
                player2_x, player2_y = move_player(
                    player2_x,
                    player2_y,
                    direction2,
                    turns_allowed2,
                    player_speed,
                )

            def control_ghost(
                ghost_obj: Ghost,
                gx: float,
                gy: float,
                gdir: int,
                speed: float,
                ghost_id: int,
            ):
                nonlocal ghost_player_direction, ghost_player_direction_command

                if ghost_is_player_controlled(ghost_id) and not ghost_obj.dead:
                    g_center_x = gx + 22
                    g_center_y = gy + 22
                    g_turns = check_position(g_center_x, g_center_y, ghost_player_direction, level)
                    if ghost_player_direction_command == 0 and g_turns[0]:
                        ghost_player_direction = 0
                    if ghost_player_direction_command == 1 and g_turns[1]:
                        ghost_player_direction = 1
                    if ghost_player_direction_command == 2 and g_turns[2]:
                        ghost_player_direction = 2
                    if ghost_player_direction_command == 3 and g_turns[3]:
                        ghost_player_direction = 3
                    nx, ny = move_player(
                        gx,
                        gy,
                        ghost_player_direction,
                        g_turns,
                        speed,
                    )
                    if nx < -30:
                        nx = WIDTH
                    elif nx > WIDTH:
                        nx -= 30
                    return nx, ny, ghost_player_direction
                else:
                    return gx, gy, gdir

            blinky_x, blinky_y, blinky_direction = control_ghost(
                blinky, blinky_x, blinky_y, blinky_direction, ghost_speeds[0], 0
            )
            if not ghost_is_player_controlled(0):
                if not blinky_dead and not blinky.in_box:
                    blinky_x, blinky_y, blinky_direction = blinky.move_blinky()
                else:
                    blinky_x, blinky_y, blinky_direction = blinky.move_clyde()

            inky_x, inky_y, inky_direction = control_ghost(
                inky, inky_x, inky_y, inky_direction, ghost_speeds[1], 1
            )
            if not ghost_is_player_controlled(1):
                if not inky_dead and not inky.in_box:
                    inky_x, inky_y, inky_direction = inky.move_inky()
                else:
                    inky_x, inky_y, inky_direction = inky.move_clyde()

            pinky_x, pinky_y, pinky_direction = control_ghost(
                pinky, pinky_x, pinky_y, pinky_direction, ghost_speeds[2], 2
            )
            if not ghost_is_player_controlled(2):
                if not pinky_dead and not pinky.in_box:
                    pinky_x, pinky_y, pinky_direction = pinky.move_pinky()
                else:
                    pinky_x, pinky_y, pinky_direction = pinky.move_clyde()

            clyde_x, clyde_y, clyde_direction = control_ghost(
                clyde, clyde_x, clyde_y, clyde_direction, ghost_speeds[3], 3
            )
            if not ghost_is_player_controlled(3):
                clyde_x, clyde_y, clyde_direction = clyde.move_clyde()
        else:
            turns_allowed = check_position(center_x, center_y, direction, level)
            if multiplayer_mode == "Co-op":
                turns_allowed2 = check_position(center2_x, center2_y, direction2, level)

        score, powerup, power_counter, eaten_ghost = check_collisions(
            score,
            powerup,
            power_counter,
            eaten_ghost,
            player_x,
            center_x,
            center_y,
            level,
        )
        if multiplayer_mode == "Co-op":
            score2, powerup, power_counter, eaten_ghost = check_collisions(
                score2,
                powerup,
                power_counter,
                eaten_ghost,
                player2_x,
                center2_x,
                center2_y,
                level,
            )

        def handle_player_hit(player_idx: int, circle: pygame.Rect | None):
            nonlocal lives, game_over, moving, startup_counter
            if circle is None:
                return
            if (
                (circle.colliderect(blinky.rect) and not blinky.dead)
                or (circle.colliderect(inky.rect) and not inky.dead)
                or (circle.colliderect(pinky.rect) and not pinky.dead)
                or (circle.colliderect(clyde.rect) and not clyde.dead)
            ):
                if lives > 0:
                    lives -= 1
                    if multiplayer_mode == "Co-op":
                        respawn_player(player_idx)
                    else:
                        soft_reset()
                else:
                    game_over = True
                    moving = False
                    startup_counter = 0

        if not powerup and not (paused or remap_mode or show_help or game_over or game_won):
            handle_player_hit(1, player_circle)
            if multiplayer_mode == "Co-op":
                handle_player_hit(2, player2_circle)

        def handle_power_collision_already_eaten(
            player_idx: int, circle: pygame.Rect | None, ghost_obj, idx: int
        ):
            nonlocal lives, game_over, moving, startup_counter
            if circle is None:
                return
            if (
                powerup
                and circle.colliderect(ghost_obj.rect)
                and eaten_ghost[idx]
                and not ghost_obj.dead
                and not (paused or remap_mode or show_help or game_over or game_won)
            ):
                if lives > 0:
                    lives -= 1
                    if multiplayer_mode == "Co-op":
                        respawn_player(player_idx)
                    else:
                        soft_reset()
                else:
                    game_over = True
                    moving = False
                    startup_counter = 0

        handle_power_collision_already_eaten(1, player_circle, blinky, 0)
        handle_power_collision_already_eaten(1, player_circle, inky, 1)
        handle_power_collision_already_eaten(1, player_circle, pinky, 2)
        handle_power_collision_already_eaten(1, player_circle, clyde, 3)

        if multiplayer_mode == "Co-op":
            handle_power_collision_already_eaten(2, player2_circle, blinky, 0)
            handle_power_collision_already_eaten(2, player2_circle, inky, 1)
            handle_power_collision_already_eaten(2, player2_circle, pinky, 2)
            handle_power_collision_already_eaten(2, player2_circle, clyde, 3)

        def eat_ghost_if_possible(
            player_idx: int, circle: pygame.Rect | None, ghost_obj, idx: int, dead_flag_name: str
        ):
            nonlocal score, score2, blinky_dead, inky_dead, pinky_dead, clyde_dead
            if circle is None:
                return
            if (
                powerup
                and circle.colliderect(ghost_obj.rect)
                and not ghost_obj.dead
                and not eaten_ghost[idx]
                and not (paused or remap_mode or show_help or game_over or game_won)
            ):
                if dead_flag_name == "blinky":
                    blinky_dead = True
                elif dead_flag_name == "inky":
                    inky_dead = True
                elif dead_flag_name == "pinky":
                    pinky_dead = True
                elif dead_flag_name == "clyde":
                    clyde_dead = True
                eaten_ghost[idx] = True
                points = (2 ** eaten_ghost.count(True)) * 100
                if player_idx == 1:
                    score += points
                else:
                    score2 += points

        eat_ghost_if_possible(1, player_circle, blinky, 0, "blinky")
        eat_ghost_if_possible(1, player_circle, inky, 1, "inky")
        eat_ghost_if_possible(1, player_circle, pinky, 2, "pinky")
        eat_ghost_if_possible(1, player_circle, clyde, 3, "clyde")

        if multiplayer_mode == "Co-op":
            eat_ghost_if_possible(2, player2_circle, blinky, 0, "blinky")
            eat_ghost_if_possible(2, player2_circle, inky, 1, "inky")
            eat_ghost_if_possible(2, player2_circle, pinky, 2, "pinky")
            eat_ghost_if_possible(2, player2_circle, clyde, 3, "clyde")

        finalize_run_if_needed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if remap_mode:
                    handle_remap_key(event.key)
                    continue

                if event.key == pygame.K_F5:
                    start_remap_mode()
                    continue

                if event.key == pygame.K_h and not (game_over or game_won):
                    show_help = not show_help
                    continue

                if event.key == pygame.K_m and not (game_over or game_won):
                    cycle_multiplayer_mode()
                    continue

                if event.key == pygame.K_g and multiplayer_mode == "Versus" and not (game_over or game_won):
                    versus_ghost_index = (versus_ghost_index + 1) % 4
                    ghost_player_direction = 0
                    ghost_player_direction_command = 0
                    continue

                if event.key == pygame.K_1:
                    apply_difficulty("easy")
                elif event.key == pygame.K_2:
                    apply_difficulty("normal")
                elif event.key == pygame.K_3:
                    apply_difficulty("hard")

                if event.key == key_bindings["restart"] and (game_over or game_won):
                    full_restart()
                    continue

                if event.key == key_bindings["pause"] and not game_over and not game_won:
                    paused = not paused
                    if paused:
                        pause_menu_index = 0
                    continue

                if paused and not game_over and not game_won:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        pause_menu_index = (pause_menu_index - 1) % len(PAUSE_MENU_ITEMS)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        pause_menu_index = (pause_menu_index + 1) % len(PAUSE_MENU_ITEMS)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        selected = PAUSE_MENU_ITEMS[pause_menu_index]
                        if selected == "Resume":
                            paused = False
                        elif selected == "Restart":
                            full_restart()
                        elif selected == "Change Difficulty":
                            names = list(DIFFICULTIES.keys())
                            idx = names.index(difficulty_name)
                            new_name = names[(idx + 1) % len(names)]
                            apply_difficulty(new_name)
                        elif selected == "Theme Mode":
                            cycle_theme_mode()
                        elif selected == "Multiplayer":
                            cycle_multiplayer_mode()
                        elif selected == "Quit":
                            running = False

                    continue

                if not (paused or remap_mode or show_help or game_over or game_won):

                    if event.key == key_bindings["move_right"]:
                        direction_command = 0
                    if event.key == key_bindings["move_left"]:
                        direction_command = 1
                    if event.key == key_bindings["move_up"]:
                        direction_command = 2
                    if event.key == key_bindings["move_down"]:
                        direction_command = 3

                    if event.key == key_bindings_p2["move_right"]:
                        if multiplayer_mode == "Co-op":
                            direction2_command = 0
                        elif multiplayer_mode == "Versus":
                            ghost_player_direction_command = 0
                    if event.key == key_bindings_p2["move_left"]:
                        if multiplayer_mode == "Co-op":
                            direction2_command = 1
                        elif multiplayer_mode == "Versus":
                            ghost_player_direction_command = 1
                    if event.key == key_bindings_p2["move_up"]:
                        if multiplayer_mode == "Co-op":
                            direction2_command = 2
                        elif multiplayer_mode == "Versus":
                            ghost_player_direction_command = 2
                    if event.key == key_bindings_p2["move_down"]:
                        if multiplayer_mode == "Co-op":
                            direction2_command = 3
                        elif multiplayer_mode == "Versus":
                            ghost_player_direction_command = 3

            if event.type == pygame.KEYUP and not remap_mode:
                if event.key == key_bindings["move_right"] and direction_command == 0:
                    direction_command = direction
                if event.key == key_bindings["move_left"] and direction_command == 1:
                    direction_command = direction
                if event.key == key_bindings["move_up"] and direction_command == 2:
                    direction_command = direction
                if event.key == key_bindings["move_down"] and direction_command == 3:
                    direction_command = direction

        if direction_command == 0 and turns_allowed[0]:
            direction = 0
        if direction_command == 1 and turns_allowed[1]:
            direction = 1
        if direction_command == 2 and turns_allowed[2]:
            direction = 2
        if direction_command == 3 and turns_allowed[3]:
            direction = 3

        if multiplayer_mode == "Co-op":
            if direction2_command == 0 and turns_allowed2[0]:
                direction2 = 0
            if direction2_command == 1 and turns_allowed2[1]:
                direction2 = 1
            if direction2_command == 2 and turns_allowed2[2]:
                direction2 = 2
            if direction2_command == 3 and turns_allowed2[3]:
                direction2 = 3

        if player_x > WIDTH:
            player_x = -47
        elif player_x < -50:
            player_x = WIDTH - 3

        if multiplayer_mode == "Co-op":
            if player2_x > WIDTH:
                player2_x = -47
            elif player2_x < -50:
                player2_x = WIDTH - 3

        if blinky.in_box and blinky_dead:
            blinky_dead = False
        if inky.in_box and inky_dead:
            inky_dead = False
        if pinky.in_box and pinky_dead:
            pinky_dead = False
        if clyde.in_box and clyde_dead:
            clyde_dead = False

        pygame.display.flip()

    pygame.quit()
