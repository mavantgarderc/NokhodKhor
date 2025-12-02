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
    difficulty_name: str,
    level_index: int,
    total_levels: int,
    remap_prompt: str | None = None,
) -> None:
    score_text = font.render(f"Score: {score}", True, "white")
    screen.blit(score_text, (10, 920))
    screen.blit(high_text, (200, 920))

    if powerup:
        pygame.draw.circle(screen, "blue", (140, 930), 15)
    for i in range(lives):
        screen.blit(
            pygame.transform.scale(player_images[0], (30, 30)),
        )

    status_text = (
        f"Level {level_index + 1}/{total_levels}  |  "
        f"Difficulty: {difficulty_name.capitalize()}"
    )
    screen.blit(status_surf, (10, 890))

    hints_text = "F5: Remap keys | 1/2/3: Easy/Normal/Hard"
    hints_surf = font.render(hints_text, True, "gray")
    screen.blit(hints_surf, (10, 870))

    if game_over:
        pygame.draw.rect(screen, "dark gray", [70, 220, 760, 260], 0, 10)
        gameover_text = font.render(
            "Game over! Restart key to play again!", True, "red"
        )

    if game_won:
        pygame.draw.rect(screen, "white", [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, "dark gray", [70, 220, 760, 260], 0, 10)
        gameover_text = font.render(
            "Victory! Restart key to play again!", True, "green"
        )
        screen.blit(gameover_text, (100, 300))

    if paused and not (game_over or game_won):
        pygame.draw.rect(screen, "white", [100, 250, 700, 200], 0, 10)
        pygame.draw.rect(screen, "darkgray", [120, 270, 660, 160], 0, 10)
        pause_text = font.render("Paused - press Pause key to resume", True, "yellow")
        screen.blit(pause_text, (150, 320))

    if remap_prompt is not None:
        screen.blit(remap_text, (150, 360))

