import pygame
from ball import Ball
from circle import Circle
from explosion import Explosion
import random

pygame.init()

screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Bouncing Ball")
screen.fill((0, 0, 0))
clock = pygame.time.Clock()
running = True

TOTAL_FRAMES = 60 * 61

position_ball_x = screen.get_width() // 2
position_ball_y = screen.get_height() // 2
radius_ball = 20
color_ball = (0, 0, 0)
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

position_circle_x = screen.get_width() // 2
position_circle_y = screen.get_height() // 2
thickness = 5
start_radius = 200
number_of_circles = 40


def generate_circles(number_of_circles, start_radius, gap):
    circles = []
    for i in range(number_of_circles):
        radius = start_radius + i * gap
        start_angle = (i * 30) % 360  # Angle de départ unique pour chaque cercle
        rotation_speed = random.uniform(0.02, 0.03)  # Vitesse de rotation aléatoire
        circle = Circle(
            position_circle_x,
            position_circle_y,
            radius,
            (255, 255, 255),  # Couleur des cercles
            thickness,  # Épaisseur du contour
            start_angle,  # Angle de départ
            gap_angle=0,
            gap_size=0.5,
        )
        circle.rotation_speed = rotation_speed
        circles.append(circle)
    return circles


gap_between_circles = 30
all_circles = generate_circles(number_of_circles, start_radius, gap_between_circles)
circles = all_circles[:20]
next_circle_index = 20
circles_to_remove = []

base_circle = circles[0]
base_circle.min_radius = 100
base_circle.shrink_rate = 0.1

explosions = []

for i in range(TOTAL_FRAMES):
    screen.fill((0, 0, 0))
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
    for circle in circles[:]:
        if circle.check_collision(ball):
            # Ajoute une explosion avant de supprimer le cercle
            # Lorsque vous créez l'explosion, utilisez une couleur plus vive :
            explosions.append(
                Explosion(
                    circle.x,
                    circle.y,
                    circle.radius,
                    (255, 000, 000),  # Bleu plus clair et visible
                )
            )
            circles.remove(circle)
            if next_circle_index < len(all_circles):
                circles.append(all_circles[next_circle_index])
                next_circle_index += 1

    # Mettez à jour et dessinez les explosions
    for explosion in explosions[:]:
        explosion.update()
        explosion.draw(screen)
        if explosion.is_done():
            explosions.remove(explosion)

    # Gérer les bords de l'écran
    if ball.x - ball.radius < 0 or ball.x + ball.radius > screen.get_width():
        ball.velocity_x = -ball.velocity_x  # Inversion parfaite
        ball.x = max(ball.radius, min(screen.get_width() - ball.radius, ball.x))

    if ball.y - ball.radius < 0 or ball.y + ball.radius > screen.get_height():
        ball.velocity_y = -ball.velocity_y  # Inversion parfaite
        ball.y = max(ball.radius, min(screen.get_height() - ball.radius, ball.y))

    if circles:
        base_circle = circles[0]
        if base_circle.radius > base_circle.min_radius:
            base_circle.radius -= base_circle.shrink_rate
            base_circle.radius = max(base_circle.radius, base_circle.min_radius)

        # Mise à jour des rayons des autres cercles
        for idx, circle in enumerate(circles):
            circle.radius = base_circle.radius + idx * gap_between_circles

    for circle in circles:
        circle.draw(screen)
    ball.draw(screen)
    ball.trail_positions.insert(0, (ball.x, ball.y))  
    if len(ball.trail_positions) > ball.max_trail_length:
        ball.trail_positions.pop()  
    pygame.display.update()

pygame.quit()
