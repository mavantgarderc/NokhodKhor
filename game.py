import copy

import pygame

from board import boards, draw_board
from config import (
    BLINKY_START,
    CLYDE_START,
    COLOR_BG,
    FONT_NAME,
    FONT_SIZE,
    FPS,
    HEIGHT,
    INKY_START,
    PINKY_START,
    PLAYER_SPEED,
    PLAYER_START_X,
    PLAYER_START_Y,
    POWERUP_DURATION_FRAMES,
    STARTUP_DELAY_FRAMES,
    WIDTH,
)
from ghosts import Ghost
from hud import draw_misc
from player import check_collisions, check_position, draw_player, move_player


def run() -> None:
    pygame.init()
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    timer = pygame.time.Clock()
    font = pygame.font.Font(FONT_NAME, FONT_SIZE)

    # Assets
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

    # Game state
    level = copy.deepcopy(boards[0])

    player_x = PLAYER_START_X
    player_y = PLAYER_START_Y
    direction = 0
    direction_command = 0
    player_speed = PLAYER_SPEED

    blinky_x, blinky_y, blinky_direction = BLINKY_START
    inky_x, inky_y, inky_direction = INKY_START
    pinky_x, pinky_y, pinky_direction = PINKY_START
    clyde_x, clyde_y, clyde_direction = CLYDE_START

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

    blinky_dead = False
    inky_dead = False
    clyde_dead = False
    pinky_dead = False

    moving = False
    ghost_speeds = [2, 2, 2, 2]
    startup_counter = 0
    lives = 3
    game_over = False
    game_won = False

    running = True

    def soft_reset() -> None:
        """Reset positions / directions / powerup state after losing a life."""
        nonlocal player_x, player_y, direction, direction_command
        nonlocal blinky_x, blinky_y, blinky_direction
        nonlocal inky_x, inky_y, inky_direction
        nonlocal pinky_x, pinky_y, pinky_direction
        nonlocal clyde_x, clyde_y, clyde_direction
        nonlocal eaten_ghost, blinky_dead, inky_dead, pinky_dead, clyde_dead
        nonlocal powerup, power_counter, startup_counter

        powerup = False
        power_counter = 0
        startup_counter = 0

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

    def full_restart() -> None:
        """Full game restart from SPACE after game over / victory."""
        nonlocal score, lives, level, game_over, game_won
        soft_reset()
        score = 0
        lives = 3
        level = copy.deepcopy(boards[0])
        game_over = False
        game_won = False

    while running:
        timer.tick(FPS)

        # Animation counter & powerup flicker
        if counter < 19:
            counter += 1
            if counter > 3:
                flicker = False
        else:
            counter = 0
            flicker = True

        # Powerup timer
        if powerup and power_counter < POWERUP_DURATION_FRAMES:
            power_counter += 1
        elif powerup and power_counter >= POWERUP_DURATION_FRAMES:
            power_counter = 0
            powerup = False
            eaten_ghost = [False, False, False, False]

        # Startup delay
        if startup_counter < STARTUP_DELAY_FRAMES and not game_over and not game_won:
            moving = False
            startup_counter += 1
        else:
            moving = True

        # Background & board
        screen.fill(COLOR_BG)
        draw_board(screen, level, flicker)

        center_x = player_x + 23
        center_y = player_y + 24

        # Ghost speeds
        if powerup:
            ghost_speeds = [1, 1, 1, 1]
        else:
            ghost_speeds = [2, 2, 2, 2]

        for idx in range(4):
            if eaten_ghost[idx]:
                ghost_speeds[idx] = 2

        if blinky_dead:
            ghost_speeds[0] = 4
        if inky_dead:
            ghost_speeds[1] = 4
        if pinky_dead:
            ghost_speeds[2] = 4
        if clyde_dead:
            ghost_speeds[3] = 4

        # Win condition
        game_won = True
        for row in level:
            if 1 in row or 2 in row:
                game_won = False
                break

        # Player
        player_circle = pygame.draw.circle(screen, "black", (center_x, center_y), 20, 2)
        draw_player(screen, player_images, counter, player_x, player_y, direction)

        # Ghosts: instantiate, update collisions, draw
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

        # HUD
        draw_misc(
            screen,
            font,
            score,
            powerup,
            lives,
            game_over,
            game_won,
            player_images,
        )

        # Targets (keep your original targeting logic, with fixed Pinky bug)
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
                # Pinky: fixed, now uses eaten_ghost[2]
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

        # Player movement
        turns_allowed = check_position(center_x, center_y, direction, level)
        if moving:
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

        # Pellet / powerups
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

        # Collisions when not powered
        if not powerup:
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

        # Collisions when powered but re-hit an already "eaten" ghost
        def handle_power_collision_already_eaten(ghost_obj, idx: int, dead_flag: bool):
            nonlocal lives, game_over, moving, startup_counter, powerup
            if (
                powerup
                and player_circle.colliderect(ghost_obj.rect)
                and eaten_ghost[idx]
                and not ghost_obj.dead
            ):
                if lives > 0:
                    lives -= 1
                    soft_reset()
                else:
                    game_over = True
                    moving = False
                    startup_counter = 0

        handle_power_collision_already_eaten(blinky, 0, blinky_dead)
        handle_power_collision_already_eaten(inky, 1, inky_dead)
        handle_power_collision_already_eaten(pinky, 2, pinky_dead)
        handle_power_collision_already_eaten(clyde, 3, clyde_dead)

        # Collisions when powered and eating ghosts
        def eat_ghost_if_possible(ghost_obj, idx: int, dead_flag_name: str):
            nonlocal score, blinky_dead, inky_dead, pinky_dead, clyde_dead
            if (
                powerup
                and player_circle.colliderect(ghost_obj.rect)
                and not ghost_obj.dead
                and not eaten_ghost[idx]
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

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    direction_command = 0
                if event.key == pygame.K_LEFT:
                    direction_command = 1
                if event.key == pygame.K_UP:
                    direction_command = 2
                if event.key == pygame.K_DOWN:
                    direction_command = 3
                if event.key == pygame.K_SPACE and (game_over or game_won):
                    full_restart()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT and direction_command == 0:
                    direction_command = direction
                if event.key == pygame.K_LEFT and direction_command == 1:
                    direction_command = direction
                if event.key == pygame.K_UP and direction_command == 2:
                    direction_command = direction
                if event.key == pygame.K_DOWN and direction_command == 3:
                    direction_command = direction

        # Direction change when allowed
        if direction_command == 0 and turns_allowed[0]:
            direction = 0
        if direction_command == 1 and turns_allowed[1]:
            direction = 1
        if direction_command == 2 and turns_allowed[2]:
            direction = 2
        if direction_command == 3 and turns_allowed[3]:
            direction = 3

        # Player wrap
        if player_x > WIDTH:
            player_x = -47
        elif player_x < -50:
            player_x = WIDTH - 3

        # Ghosts re-enter box after being eaten
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
