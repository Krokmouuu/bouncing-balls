import pygame
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
radius_ball = 40
color_ball = (0, 0, 255)
border_color_ball = (255, 255, 255)


start_angle = 0
stop_angle = math.pi / 0.6  # Example: quarter-circle

print(start_angle, stop_angle)

for i in range(TOTAL_FRAMES):
    clock.tick(60)  # Limiter à 60 FPS
    for event in pygame.event.get():
        if (
            event.type == pygame.QUIT
            or event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
        ):
            running = False
    if not running:
        break

    screen.fill((0, 0, 0))

    start_angle += 0.060
    stop_angle += 0.060
    pygame.draw.arc(screen, (255, 0, 0), (900, 500, 500, 500), start_angle, stop_angle, 5)

    pygame.display.update()

pygame.quit()
