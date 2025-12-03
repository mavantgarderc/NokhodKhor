import copy

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
    DIFFICULTIES,
    FONT_NAME,
    FONT_SIZE,
    FPS,
    HEIGHT,
    INKY_START,
    PINKY_START,
    PLAYER_START_X,
    PLAYER_START_Y,
    STARTUP_DELAY_FRAMES,
    WIDTH,
)
from .ghosts import Ghost
from .hud import draw_misc
from .player import check_collisions, check_position, draw_player, move_player
from .scores import (
    get_high_score,
    load_high_scores,
    maybe_update_high_score,
    save_high_scores,
)


def run() -> None:
    pygame.init()
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    timer = pygame.time.Clock()
    font = pygame.font.Font(FONT_NAME, FONT_SIZE)

    player_images = []
    for i in range(1, 5):
        player_images.append(
            pygame.transform.scale(
                pygame.image.load(f"assets/player_images/{i}.png"), (40, 40)
            )
        )
    blinky_img = pygame.transform.scale(
        pygame.image.load("assets/ghost_images/red.png"), (42, 42)
    )
    pinky_img = pygame.transform.scale(
        pygame.image.load("assets/ghost_images/pink.png"), (42, 42)
    )
    inky_img = pygame.transform.scale(
        pygame.image.load("assets/ghost_images/blue.png"), (42, 42)
    )
    clyde_img = pygame.transform.scale(
        pygame.image.load("assets/ghost_images/orange.png"), (42, 42)
    )
    spooked_img = pygame.transform.scale(
        pygame.image.load("assets/ghost_images/powerup.png"), (42, 42)
    )
    dead_img = pygame.transform.scale(
        pygame.image.load("assets/ghost_images/dead.png"), (42, 42)
    )

    difficulty_name = DEFAULT_DIFFICULTY
    difficulty = DIFFICULTIES[difficulty_name]

    player_speed = difficulty["player_speed"]
    powerup_duration_frames = difficulty["powerup_duration"]
    max_lives = difficulty["lives"]

    key_bindings = DEFAULT_KEY_BINDINGS.copy()

    high_scores = load_high_scores()
    current_high_score = get_high_score(high_scores, difficulty_name)
    run_recorded = False

    PAUSE_MENU_ITEMS = ["Resume", "Restart", "Change Difficulty", "Quit"]
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

    blinky_x, blinky_y, blinky_direction = BLINKY_START
    inky_x, inky_y, inky_direction = INKY_START
    pinky_x, pinky_y, pinky_direction = PINKY_START
    clyde_x, clyde_y, clyde_direction = CLYDE_START

    blinky_dead = False
    inky_dead = False
    clyde_dead = False
    pinky_dead = False

    counter = 0
    flicker = False
    turns_allowed = [False, False, False, False]

    score = 0
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

    running = True

    def apply_difficulty(name: str) -> None:
        nonlocal difficulty_name, difficulty
        nonlocal player_speed, powerup_duration_frames, max_lives
        nonlocal current_high_score
        difficulty_name = name
        difficulty = DIFFICULTIES[difficulty_name]
        player_speed = difficulty["player_speed"]
        powerup_duration_frames = difficulty["powerup_duration"]
        max_lives = difficulty["lives"]
        current_high_score = get_high_score(high_scores, difficulty_name)

    def soft_reset() -> None:
        nonlocal player_x, player_y, direction, direction_command
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

        blinky_x, blinky_y, blinky_direction = BLINKY_START
        inky_x, inky_y, inky_direction = INKY_START
        pinky_x, pinky_y, pinky_direction = PINKY_START
        clyde_x, clyde_y, clyde_direction = CLYDE_START

        eaten_ghost = [False, False, False, False]
        blinky_dead = False
        inky_dead = False
        pinky_dead = False
        clyde_dead = False

    def load_level(idx: int) -> None:
        nonlocal level, current_level_index
        current_level_index = idx
        level = copy.deepcopy(boards[current_level_index])
        soft_reset()

    def full_restart() -> None:
        nonlocal score, lives, level, game_over, game_won, run_recorded
        score = 0
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
        nonlocal run_recorded, current_high_score
        if (game_over or game_won) and not run_recorded:
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

            if (
                startup_counter < STARTUP_DELAY_FRAMES
                and not game_over
                and not game_won
            ):
                moving = False
                startup_counter += 1
            else:
                moving = True

        screen.fill(COLOR_BG)
        draw_board(screen, level, flicker)

        center_x = player_x + 23
        center_y = player_y + 24

        if powerup:
            ghost_speeds = [difficulty["frightened_speed"]] * 4
        else:
            ghost_speeds = [difficulty["ghost_speed"]] * 4

        for idx in range(4):
            if eaten_ghost[idx]:
                ghost_speeds[idx] = difficulty["ghost_speed"]

        if blinky_dead:
            ghost_speeds[0] = difficulty["eaten_speed"]
        if inky_dead:
            ghost_speeds[1] = difficulty["eaten_speed"]
        if pinky_dead:
            ghost_speeds[2] = difficulty["eaten_speed"]
        if clyde_dead:
            ghost_speeds[3] = difficulty["eaten_speed"]

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
            current_high_score,
            powerup,
            lives,
            game_over,
            game_won,
            player_images,
            paused,
            pause_menu_index,
            difficulty_name,
            current_level_index,
            total_levels,
            show_help,
            bindings_display,
            remap_prompt,
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
            nonlocal powerup, eaten_ghost, player_x, player_y
            if player_x < 450:
                runaway_x = 900
            else:
                runaway_x = 0
            if player_y < 450:
                runaway_y = 900
            else:
                runaway_y = 0
            return_target = (380, 400)
            if powerup:
                if not blinky.dead and not eaten_ghost[0]:
                    blink_target = (runaway_x, runaway_y)
                elif not blinky.dead and eaten_ghost[0]:
                    if 340 < blink_x < 560 and 340 < blink_y < 500:
                        blink_target = (400, 100)
                    else:
                        blink_target = (player_x, player_y)
                else:
                    blink_target = return_target
                if not inky.dead and not eaten_ghost[1]:
                    ink_target = (runaway_x, player_y)
                elif not inky.dead and eaten_ghost[1]:
                    if 340 < ink_x < 560 and 340 < ink_y < 500:
                        ink_target = (400, 100)
                    else:
                        ink_target = (player_x, player_y)
                else:
                    ink_target = return_target
                if not pinky.dead and not eaten_ghost[2]:
                    pink_target = (player_x, runaway_y)
                elif not pinky.dead and eaten_ghost[2]:
                    if 340 < pink_x < 560 and 340 < pink_y < 500:
                        pink_target = (400, 100)
                    else:
                        pink_target = (player_x, player_y)
                else:
                    pink_target = return_target
                if not clyde.dead and not eaten_ghost[3]:
                    clyd_target = (450, 450)
                elif not clyde.dead and eaten_ghost[3]:
                    if 340 < clyd_x < 560 and 340 < clyd_y < 500:
                        clyd_target = (400, 100)
                    else:
                        clyd_target = (player_x, player_y)
                else:
                    clyd_target = return_target
            else:
                if not blinky.dead:
                    if 340 < blink_x < 560 and 340 < blink_y < 500:
                        blink_target = (400, 100)
                    else:
                        blink_target = (player_x, player_y)
                else:
                    blink_target = return_target
                if not inky.dead:
                    if 340 < ink_x < 560 and 340 < ink_y < 500:
                        ink_target = (400, 100)
                    else:
                        ink_target = (player_x, player_y)
                else:
                    ink_target = return_target
                if not pinky.dead:
                    if 340 < pink_x < 560 and 340 < pink_y < 500:
                        pink_target = (400, 100)
                    else:
                        pink_target = (player_x, player_y)
                else:
                    pink_target = return_target
                if not clyde.dead:
                    if 340 < clyd_x < 560 and 340 < clyd_y < 500:
                        clyd_target = (400, 100)
                    else:
                        clyd_target = (player_x, player_y)
                else:
                    clyd_target = return_target
            return [blink_target, ink_target, pink_target, clyd_target]

        targets = get_targets(
            blinky_x, blinky_y, inky_x, inky_y, pinky_x, pinky_y, clyde_x, clyde_y
        )

        can_update_positions = (
            moving
            and not paused
            and not remap_mode
            and not show_help
            and not game_over
            and not game_won
        )

        if can_update_positions:
            turns_allowed = check_position(center_x, center_y, direction, level)
            player_x, player_y = move_player(
                player_x, player_y, direction, turns_allowed, player_speed
            )

            if not blinky_dead and not blinky.in_box:
                blinky_x, blinky_y, blinky_direction = blinky.move_blinky()
            else:
                blinky_x, blinky_y, blinky_direction = blinky.move_clyde()
            if not pinky_dead and not pinky.in_box:
                pinky_x, pinky_y, pinky_direction = pinky.move_pinky()
            else:
                pinky_x, pinky_y, pinky_direction = pinky.move_clyde()
            if not inky_dead and not inky.in_box:
                inky_x, inky_y, inky_direction = inky.move_inky()
            else:
                inky_x, inky_y, inky_direction = inky.move_clyde()
            clyde_x, clyde_y, clyde_direction = clyde.move_clyde()
        else:
            turns_allowed = check_position(center_x, center_y, direction, level)

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

        if not powerup and not (
            paused or remap_mode or show_help or game_over or game_won
        ):
            if (
                (player_circle.colliderect(blinky.rect) and not blinky.dead)
                or (player_circle.colliderect(inky.rect) and not inky.dead)
                or (player_circle.colliderect(pinky.rect) and not pinky.dead)
                or (player_circle.colliderect(clyde.rect) and not clyde.dead)
            ):
                if lives > 0:
                    lives -= 1
                    soft_reset()
                else:
                    game_over = True
                    moving = False
                    startup_counter = 0

        def handle_power_collision_already_eaten(ghost_obj, idx: int):
            nonlocal lives, game_over, moving, startup_counter
            if (
                powerup
                and player_circle.colliderect(ghost_obj.rect)
                and eaten_ghost[idx]
                and not ghost_obj.dead
                and not (paused or remap_mode or show_help or game_over or game_won)
            ):
                if lives > 0:
                    lives -= 1
                    soft_reset()
                else:
                    game_over = True
                    moving = False
                    startup_counter = 0

        handle_power_collision_already_eaten(blinky, 0)
        handle_power_collision_already_eaten(inky, 1)
        handle_power_collision_already_eaten(pinky, 2)
        handle_power_collision_already_eaten(clyde, 3)

        def eat_ghost_if_possible(ghost_obj, idx: int, dead_flag_name: str):
            nonlocal score, blinky_dead, inky_dead, pinky_dead, clyde_dead
            if (
                powerup
                and player_circle.colliderect(ghost_obj.rect)
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
                score += (2 ** eaten_ghost.count(True)) * 100

        eat_ghost_if_possible(blinky, 0, "blinky")
        eat_ghost_if_possible(inky, 1, "inky")
        eat_ghost_if_possible(pinky, 2, "pinky")
        eat_ghost_if_possible(clyde, 3, "clyde")

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

                if event.key == pygame.K_1:
                    apply_difficulty("easy")
                elif event.key == pygame.K_2:
                    apply_difficulty("normal")
                elif event.key == pygame.K_3:
                    apply_difficulty("hard")

                if event.key == key_bindings["restart"] and (game_over or game_won):
                    full_restart()
                    continue

                if (
                    event.key == key_bindings["pause"]
                    and not game_over
                    and not game_won
                ):
                    paused = not paused
                    if paused:
                        pause_menu_index = 0
                    continue

                if paused and not game_over and not game_won:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        pause_menu_index = (pause_menu_index - 1) % len(
                            PAUSE_MENU_ITEMS
                        )
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        pause_menu_index = (pause_menu_index + 1) % len(
                            PAUSE_MENU_ITEMS
                        )
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

        if player_x > WIDTH:
            player_x = -47
        elif player_x < -50:
            player_x = WIDTH - 3

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
