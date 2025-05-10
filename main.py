import pygame
from ball import Ball
from circle import Circle
import math

pygame.init()

screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Bouncing Ball")
screen.fill((0, 0, 0))
clock = pygame.time.Clock()
running = True

TOTAL_FRAMES = 60 * 61

position_ball_x = 540
position_ball_y = 200
radius_ball = 20
color_ball = (0, 0, 255)
border_color_ball = (255, 255, 255)


def reset_ball():
    return Ball(
        position_ball_x,
        position_ball_y,
        radius_ball,
        color_ball,
        border_color_ball,
        radius_ball + 2,
    )


ball = reset_ball()
ball.prev_x = ball.x
ball.prev_y = ball.y
ball.x += ball.velocity_x
ball.y += ball.velocity_y

circle = Circle(900, 500, 500, (255, 0, 0), 5, 100, gap_angle=0, gap_size=0.5)


for i in range(TOTAL_FRAMES):
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            ball = reset_ball()

    if not running:
        break

    # Sauvegarder la position avant mise à jour
    ball.prev_x = ball.x
    ball.prev_y = ball.y

    # Mettre à jour la position
    ball.velocity_y += ball.gravity
    ball.x += ball.velocity_x
    ball.y += ball.velocity_y

    # Vérifier les collisions
    circle.check_collision(ball)

    # Gérer les bords de l'écran
    if ball.x - ball.radius < 0 or ball.x + ball.radius > screen.get_width():
        ball.velocity_x *= -0.8
        ball.x = max(ball.radius, min(screen.get_width() - ball.radius, ball.x))
    if ball.y - ball.radius < 0 or ball.y + ball.radius > screen.get_height():
        ball.velocity_y *= -0.8
        ball.y = max(ball.radius, min(screen.get_height() - ball.radius, ball.y))

    screen.fill((0, 0, 0))
    circle.draw(screen)
    ball.draw(screen)
    pygame.display.update()

pygame.quit()
