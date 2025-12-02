import pygame


def draw_misc(
    screen: pygame.Surface,
    font: pygame.font.Font,
    score: int,
    powerup: bool,
    lives: int,
    game_over: bool,
    game_won: bool,
    player_images,
) -> None:
    """Draw score, powerup indicator, lives, and end-game messages."""
    score_text = font.render(f"Score: {score}", True, "white")
    screen.blit(score_text, (10, 920))

    if powerup:
        pygame.draw.circle(screen, "blue", (140, 930), 15)

    for i in range(lives):
        screen.blit(
            pygame.transform.scale(player_images[0], (30, 30)),
            (650 + i * 40, 915),
        )

    if game_over:
        pygame.draw.rect(screen, "white", [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, "dark gray", [70, 220, 760, 260], 0, 10)
        gameover_text = font.render("Game over! Space bar to restart!", True, "red")
        screen.blit(gameover_text, (100, 300))

    if game_won:
        pygame.draw.rect(screen, "white", [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, "dark gray", [70, 220, 760, 260], 0, 10)
        gameover_text = font.render("Victory! Space bar to restart!", True, "green")
        screen.blit(gameover_text, (100, 300))
