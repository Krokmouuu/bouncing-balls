import pygame
from ball import Ball
from circle import Circle
from explosion import Explosion
import random
from colors import colors
import argparse

parser = argparse.ArgumentParser(description="Bouncing Ball Game")
parser.add_argument(
    "--ball_color",
    type=str,
    default="black",
    help="Couleur de la balle (nom de couleur)",
)
parser.add_argument(
    "--circle_color",
    type=str,
    default="white",
    help="Couleur des cercles (nom de couleur)",
)
parser.add_argument(
    "--explosion_color",
    type=str,
    default="red",
    help="Couleur de l'explosion (nom de couleur)",
)
parser.add_argument(
    "--balls",
    type=str,
    default="1",
    help="Nombre de balle",
)
args = parser.parse_args()

pygame.init()

screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Bouncing Ball")
screen.fill((0, 0, 0))
clock = pygame.time.Clock()
running = True

TOTAL_FRAMES = 60 * 65

position_ball_x = screen.get_width() // 2
position_ball_y = screen.get_height() // 2
radius_ball = 20
color_ball = colors.get(
    args.ball_color, (255, 255, 255)
)  # Utilise la couleur spécifiée ou noir par défaut
border_color_ball = (255, 255, 255)

num_balls = int(args.balls)  # Nombre de balles

if num_balls > 5:
    print("Le nombre de balles doit être inférieur ou égal à 5.")
    running = False

ball_colors = random.sample(
    list(colors.values()), num_balls
)  # Couleurs uniques pour chaque balle


def reset_ball(x_offset=0, ball_color=(255, 255, 255)):
    """Créer une balle avec un décalage horizontal et une couleur spécifique."""
    return Ball(
        position_ball_x + x_offset,
        position_ball_y,
        radius_ball,
        ball_color,
        border_color_ball,
        radius_ball + 2,
    )


balls = [
    reset_ball(
        x_offset=(-100 * (num_balls // 2)) + (i * 100),  # Décalage horizontal
        ball_color=ball_colors[i],  # Couleur unique pour chaque balle
    )
    for i in range(num_balls)
]

position_circle_x = screen.get_width() // 2
position_circle_y = screen.get_height() // 2
thickness = 5
start_radius = 200
number_of_circles = 40
circle_color = colors.get(args.circle_color, (0, 0, 0))  # Couleur des cercles


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
            circle_color,  # Couleur des cercles
            thickness,  # Épaisseur du contour
            start_angle,  # Angle de départ
            gap_angle=3,
            gap_size=0.7,
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
explosion_color = colors.get(
    args.explosion_color, (255, 0, 0)
)  # Couleur des explosions

for i in range(TOTAL_FRAMES):
    screen.fill((0, 0, 0))
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            balls = [
            reset_ball(
                x_offset=(-100 * (num_balls // 2)) + (i * 100),  # Décalage horizontal
                ball_color=ball_colors[i],  # Couleur unique pour chaque balle
            )
            for i in range(num_balls)
    ]

    if not running:
        break

    for ball in balls:
        # Sauvegarder la position avant mise à jour
        ball.prev_x = ball.x
        ball.prev_y = ball.y

        # Mettre à jour la position
        ball.velocity_y += ball.gravity
        ball.x += ball.velocity_x
        ball.y += ball.velocity_y

        # Gérer les bords de l'écran
        if ball.x - ball.radius < 0 or ball.x + ball.radius > screen.get_width():
            ball.velocity_x = -ball.velocity_x
            ball.x = max(ball.radius, min(screen.get_width() - ball.radius, ball.x))

        if ball.y - ball.radius < 0 or ball.y + ball.radius > screen.get_height():
            ball.velocity_y = -ball.velocity_y
            ball.y = max(ball.radius, min(screen.get_height() - ball.radius, ball.y))

        # Vérifier les collisions avec les cercles
        for circle in circles[:]:
            if circle.check_collision(ball):
                explosions.append(
                    Explosion(
                        circle.x,
                        circle.y,
                        circle.radius,
                        explosion_color,
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

    for ball in balls:
        ball.draw(screen)
        ball.trail_positions.insert(0, (ball.x, ball.y))
        if len(ball.trail_positions) > ball.max_trail_length:
            ball.trail_positions.pop()

    elapsed_time = (TOTAL_FRAMES - i) // 60
    font = pygame.font.Font(None, 40)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    timer_text = font.render(f"{minutes:02}:{seconds:02}", True, (0, 0, 0))
    if elapsed_time <= 8:
        shake_x = random.randint(-5, 5)  # Déplacement horizontal aléatoire
        shake_y = random.randint(-5, 5)  # Déplacement vertical aléatoire
    else:
        shake_x = 0
        shake_y = 0

    timer_rect = pygame.Rect(
        screen.get_width() // 2 - 30 + shake_x,  # Ajout du shake horizontal
        screen.get_height() // 2 + 400 + shake_y,  # Ajout du shake vertical
        90,
        45,
    )
    pygame.draw.rect(screen, (255, 255, 255), timer_rect)
    screen.blit(timer_text, (timer_rect.x + 10, timer_rect.y + 10))

    pygame.display.update()

pygame.quit()
