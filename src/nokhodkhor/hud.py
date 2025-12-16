import pygame

GHOST_NAMES = ["Blinky", "Inky", "Pinky", "Clyde"]


def draw_misc(
    screen: pygame.Surface,
    font: pygame.font.Font,
    score_p1: int,
    score_p2: int,
    high_score: int,
    powerup: bool,
    lives: int,
    game_over: bool,
    game_won: bool,
    player_images,
    paused: bool,
    pause_menu_index: int,
    difficulty_name: str,
    theme_mode: str,
    level_index: int,
    total_levels: int,
    show_help: bool,
    bindings_display: list[tuple[str, str]] | None,
    remap_prompt: str | None = None,
    multiplayer_mode: str = "1P",
    versus_ghost_index: int = 0,
) -> None:

    p1_text = font.render(f"P1: {score_p1}", True, "white")
    screen.blit(p1_text, (10, 920))

    if multiplayer_mode in ("Co-op", "Versus"):
        p2_text = font.render(f"P2: {score_p2}", True, "white")
        screen.blit(p2_text, (200, 920))

    high_text = font.render(f"High: {high_score}", True, "yellow")
    screen.blit(high_text, (390, 920))

    if powerup:
        pygame.draw.circle(screen, "blue", (140, 930), 15)

    for i in range(lives):
        screen.blit(
            pygame.transform.scale(player_images[0], (30, 30)),
            (650 + i * 40, 915),
        )

    mode_extra = ""
    if multiplayer_mode == "Versus":
        ghost_name = GHOST_NAMES[versus_ghost_index]
        mode_extra = f" | Versus: P2={ghost_name}"
    status_text = (
        f"Level {level_index + 1}/{total_levels}  |  "
        f"Difficulty: {difficulty_name.capitalize()}  |  "
        f"Theme: {theme_mode.capitalize()}  |  "
        f"Mode: {multiplayer_mode}{mode_extra}"
    )
    status_surf = font.render(status_text, True, "white")
    screen.blit(status_surf, (10, 890))

    hints_text = "H: Help | F5: Remap | 1/2/3: Difficulty | M: Cycle mode | G: Change P2 ghost"
    hints_surf = font.render(hints_text, True, "gray")
    screen.blit(hints_surf, (10, 870))

    if game_over:
        pygame.draw.rect(screen, "white", [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, "dark gray", [70, 220, 760, 260], 0, 10)
        gameover_text = font.render("Game over! Restart key to play again!", True, "red")
        screen.blit(gameover_text, (100, 300))

    if game_won:
        pygame.draw.rect(screen, "white", [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, "dark gray", [70, 220, 760, 260], 0, 10)
        gameover_text = font.render("Victory! Restart key to play again!", True, "green")
        screen.blit(gameover_text, (100, 300))

    if remap_prompt is not None:
        pygame.draw.rect(screen, "white", [100, 250, 700, 200], 0, 10)
        pygame.draw.rect(screen, "darkgray", [120, 270, 660, 160], 0, 10)
        title_text = font.render("Remapping controls", True, "cyan")
        screen.blit(title_text, (150, 290))
        remap_text = font.render(f"Press key for: {remap_prompt}", True, "cyan")
        screen.blit(remap_text, (150, 330))
        cancel_text = font.render("ESC to cancel remap", True, "gray")
        screen.blit(cancel_text, (150, 370))
        return

    if show_help and not (game_over or game_won):
        pygame.draw.rect(screen, "white", [100, 150, 700, 500], 0, 10)
        pygame.draw.rect(screen, "darkgray", [120, 170, 660, 460], 0, 10)

        title_text = font.render("Controls (P1 + general)", True, "yellow")
        screen.blit(title_text, (150, 190))

        if bindings_display is None:
            bindings_display = []

        base_y = 230
        for idx, (label, key_name) in enumerate(bindings_display):
            line = f"{label}: {key_name.upper()}"
            text_surf = font.render(line, True, "white")
            screen.blit(text_surf, (150, base_y + idx * 30))

        extra_lines = [
            "P2 Movement: W/A/S/D",
            "Modes: 1P, Co-op (2 Pac-Men), Versus (P2 controls a ghost)",
        ]
        for j, line in enumerate(extra_lines):
            text_surf = font.render(line, True, "white")
            screen.blit(text_surf, (150, base_y + len(bindings_display) * 30 + 20 + j * 30))

        hint_text = font.render("Press H to close this screen", True, "gray")
        screen.blit(
            hint_text,
            (150, base_y + len(bindings_display) * 30 + 20 + len(extra_lines) * 30 + 10),
        )
        return

    if paused and not (game_over or game_won):
        pygame.draw.rect(screen, "white", [180, 200, 540, 320], 0, 10)
        pygame.draw.rect(screen, "darkgray", [200, 220, 500, 280], 0, 10)

        title_text = font.render("Paused", True, "yellow")
        screen.blit(title_text, (360, 235))

        menu_items = [
            "Resume",
            "Restart",
            "Change Difficulty",
            "Theme Mode",
            "Multiplayer",
            "Quit",
        ]

        base_y = 280
        for idx, label in enumerate(menu_items):
            color = "yellow" if idx == pause_menu_index else "white"
            text_surf = font.render(label, True, color)
            screen.blit(text_surf, (260, base_y + idx * 40))

        hint_text = font.render("Use ↑/↓ + Enter", True, "gray")
        screen.blit(hint_text, (260, base_y + len(menu_items) * 40 + 10))
