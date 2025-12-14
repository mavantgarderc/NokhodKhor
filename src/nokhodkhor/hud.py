import pygame


def draw_misc(
    screen: pygame.Surface,
    font: pygame.font.Font,
    score: int,
    high_score: int,
    powerup: bool,
    lives: int,
    game_over: bool,
    game_won: bool,
    player_images,
    paused: bool,
    pause_menu_index: int,
    difficulty_name: str,
    level_index: int,
    total_levels: int,
    show_help: bool,
    bindings_display: list[tuple[str, str]] | None,
    remap_prompt: str | None = None,
) -> None:

    score_text = font.render(f"Score: {score}", True, "white")
    high_text = font.render(f"High: {high_score}", True, "yellow")
    screen.blit(score_text, (10, 920))
    screen.blit(high_text, (200, 920))

    if powerup:
        pygame.draw.circle(screen, "blue", (140, 930), 15)

    for i in range(lives):
        screen.blit(
            pygame.transform.scale(player_images[0], (30, 30)),
            (650 + i * 40, 915),
        )

    status_text = (
        f"Level {level_index + 1}/{total_levels}  |  " f"Difficulty: {difficulty_name.capitalize()}"
    )
    status_surf = font.render(status_text, True, "white")
    screen.blit(status_surf, (10, 890))

    hints_text = "H: Help/Controls | F5: Remap keys | 1/2/3: Easy/Normal/Hard"
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

        title_text = font.render("Controls", True, "yellow")
        screen.blit(title_text, (150, 190))

        if bindings_display is None:
            bindings_display = []

        base_y = 230
        for idx, (label, key_name) in enumerate(bindings_display):
            line = f"{label}: {key_name.upper()}"
            text_surf = font.render(line, True, "white")
            screen.blit(text_surf, (150, base_y + idx * 30))

        hint_text = font.render("Press H to close this screen", True, "gray")
        screen.blit(hint_text, (150, base_y + len(bindings_display) * 30 + 20))
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
            "Quit",
        ]

        base_y = 280
        for idx, label in enumerate(menu_items):
            color = "yellow" if idx == pause_menu_index else "white"
            text_surf = font.render(label, True, color)
            screen.blit(text_surf, (260, base_y + idx * 40))

        hint_text = font.render("Use / + Enter", True, "gray")
        screen.blit(hint_text, (260, base_y + len(menu_items) * 40 + 10))
