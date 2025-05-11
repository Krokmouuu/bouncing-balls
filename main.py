import pygame
from ball import Ball
from circle import Circle
from explosion import Explosion, Vaporization
import random
from colors import colors
import argparse
import math

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
    "--balls",
    type=str,
    default="1",
    help="Nombre de balle",
)
parser.add_argument(
    "--text1",
    type=str,
    default="",
    help="Texte à afficher sur la boule 1",
)
parser.add_argument(
    "--text2",
    type=str,
    default="",
    help="Texte à afficher sur la boule 2",
)
parser.add_argument(
    "--text3",
    type=str,
    default="",
    help="Texte à afficher sur la boule 3",
)
parser.add_argument(
    "--text4",
    type=str,
    default="",
    help="Texte à afficher sur la boule 5",
)
parser.add_argument(
    "--text5",
    type=str,
    default="",
    help="Texte à afficher sur la boule 5",
)
(
    parser.add_argument(
        "--title",
        type=str,
        default="",
        help="Titre",
    ),
)
args = parser.parse_args()

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
border_color_ball = (255, 255, 255)

num_balls = int(args.balls)  # Nombre de balles

if num_balls > 5:
    print("Le nombre de balles doit être inférieur ou égal à 5.")
    running = False

ball_colors = random.sample(
    list(colors.values()), num_balls
)  # Couleurs uniques pour chaque balle


def check_ball_collision(ball1, ball2):
    """Vérifie si deux balles se heurtent."""
    dx = ball1.x - ball2.x
    dy = ball1.y - ball2.y
    distance = math.sqrt(dx**2 + dy**2)
    return distance < (ball1.radius + ball2.radius)


def resolve_ball_collision(ball1, ball2):
    """Résout la collision entre deux balles."""
    dx = ball1.x - ball2.x
    dy = ball1.y - ball2.y
    distance = math.sqrt(dx**2 + dy**2)

    if distance == 0:  # Évite la division par zéro
        return

    # Calculer les vecteurs de collision
    overlap = 0.5 * (distance - ball1.radius - ball2.radius)
    ball1.x -= overlap * (dx / distance)
    ball1.y -= overlap * (dy / distance)
    ball2.x += overlap * (dx / distance)
    ball2.y += overlap * (dy / distance)

    # Calculer les nouvelles vitesses après collision
    nx = dx / distance
    ny = dy / distance
    p = (
        2
        * (
            ball1.velocity_x * nx
            + ball1.velocity_y * ny
            - ball2.velocity_x * nx
            - ball2.velocity_y * ny
        )
        / (ball1.radius + ball2.radius)
    )

    ball1.velocity_x -= p * ball2.radius * nx
    ball1.velocity_y -= p * ball2.radius * ny
    ball2.velocity_x += p * ball1.radius * nx
    ball2.velocity_y += p * ball1.radius * ny


def reset_ball(x_offset=0, ball_color=(255, 255, 255), text=""):
    """Créer une balle avec un décalage horizontal et une couleur spécifique."""
    return Ball(
        position_ball_x + x_offset,
        position_ball_y,
        radius_ball,
        ball_color,
        random.uniform(-5, 5),  # Vitesse horizontale aléatoire
        random.uniform(-5, 5),  # Vitesse verticale aléatoire
        border_color_ball,
        radius_ball + 2,
        text=text,
    )


ball_texts = [
    args.text1,
    args.text2,
    args.text3,
    args.text4,
    args.text5,
]  # Textes des balles

balls = [
    reset_ball(
        x_offset=(-100 * (num_balls // 2)) + (i * 100),  # Décalage horizontal
        ball_color=ball_colors[i],  # Couleur unique pour chaque balle
        text=ball_texts[i] if i < len(ball_texts) else "",  # Texte pour chaque balle
    )
    for i in range(num_balls)
]

position_circle_x = screen.get_width() // 2
position_circle_y = screen.get_height() // 2
thickness = 5
if num_balls >= 4:
    start_radius = 250
    number_of_circles = 70
elif num_balls == 1:
    number_of_circles = 40
else:
    start_radius = 200
    number_of_circles = 55
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
circles = all_circles[:15]
next_circle_index = 20
circles_to_remove = []

base_circle = circles[0]
base_circle.min_radius = 100
base_circle.shrink_rate = 0.1

explosions = []

start_time = pygame.time.get_ticks()  # Temps de départ en millisecondes
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
                    x_offset=(-100 * (num_balls // 2))
                    + (i * 100),  # Décalage horizontal
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
                # Ajouter une explosion
                explosions.append(
                    Explosion(
                        circle.x,
                        circle.y,
                        circle.radius,
                        ball.color,
                    )
                )
                # Ajouter une vaporisation
                explosions.append(
                    Vaporization(
                        circle.x,
                        circle.y,
                        circle.radius,
                        ball.color,  # Utiliser la couleur du cercle
                    )
                )
                circles.remove(circle)
                ball.circles_destroyed += 1
                ball.shake_frames = 4
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

    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            if check_ball_collision(balls[i], balls[j]):
                resolve_ball_collision(balls[i], balls[j])
    for ball in balls:
        ball.draw(screen)
        ball.trail_positions.insert(0, (ball.x, ball.y))
        if len(ball.trail_positions) > ball.max_trail_length:
            ball.trail_positions.pop()

    font = pygame.font.Font(None, 40)
    elapsed_time_ms = pygame.time.get_ticks() - start_time
    remaining_seconds = max(0, (TOTAL_FRAMES // 60) - (elapsed_time_ms // 1000))

    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    timer_text = font.render(f"{minutes:02}:{seconds:02}", True, (0, 0, 0))

    # Ajout d'un effet de "shake" si le temps restant est inférieur ou égal à 8 secondes
    if remaining_seconds <= 8:
        shake_x = random.randint(-5, 5)
        shake_y = random.randint(-5, 5)
    else:
        shake_x = 0
        shake_y = 0

    # Position et affichage du timer
    timer_rect = pygame.Rect(
        screen.get_width() // 2 - 45 + shake_x,  # Ajustement horizontal
        screen.get_height() // 2 + 400 + shake_y,  # Ajustement vertical
        90,
        45,
    )
    pygame.draw.rect(screen, (255, 255, 255), timer_rect)
    screen.blit(timer_text, (timer_rect.x + 10, timer_rect.y + 10))

    # Affichage du titre
    if args.title != "":
        text = font.render(args.title, True, (0, 0, 0))  # Texte en noir
        rect_x = screen.get_width() // 2 - 150  # Position horizontale
        rect_y = 50  # Position verticale
        rect_width = 350  # Largeur
        rect_height = 80  # Hauteur
        pygame.draw.rect(
            screen, (255, 255, 255), (rect_x, rect_y, rect_width, rect_height)
        )

        font = pygame.font.Font(None, 40)  # Taille de la police
        text_rect = text.get_rect(
            center=(rect_x + rect_width // 2, rect_y + rect_height // 2)
        )
        screen.blit(text, text_rect)

    if len(balls) > 1:
        # Afficher les rectangles pour 2 à 5 balles
        total_width = (
            len(balls[:5]) * 150
        )  # Largeur totale des rectangles avec espacement
        start_x = (
            screen.get_width() // 2 - total_width // 2
        )  # Point de départ pour centrer

        for i, ball in enumerate(balls[:5]):  # Limiter à un maximum de 5 balles
            if ball.text != "":
                # Définir les dimensions et la position du rectangle
                rect_x = start_x + i * 200  # Espacement horizontal entre les rectangles
                rect_y = 150  # Position verticale sous le titre
                rect_width = 150  # Largeur
                rect_height = 50  # Hauteur

                # Ajoutez un effet de "shake" si `shake_frames` est actif
                if ball.shake_frames > 0:
                    shake_x = random.randint(-5, 5)
                    shake_y = random.randint(-5, 5)
                    ball.shake_frames -= 1  # Réduisez le compteur de frames
                else:
                    shake_x = 0
                    shake_y = 0

                # Dessiner le rectangle de fond
                pygame.draw.rect(
                    screen,
                    (255, 255, 255),
                    (rect_x + shake_x, rect_y + shake_y, rect_width, rect_height),
                )

                # Rendre le texte de la balle
                text = font.render(ball.text, True, ball_colors[i])
                text_rect = text.get_rect(
                    center=(rect_x + rect_width // 2 - 20 + shake_x, rect_y + rect_height // 2 + shake_y)
                )

                # Rendre le ":" entre le texte et le compteur
                colon_text = font.render(":", True, ball_colors[i])
                colon_rect = colon_text.get_rect(
                    center=(
                        rect_x + rect_width // 2 + 17 + shake_x,
                        rect_y + rect_height // 2 - 1 + shake_y,
                    )
                )

                # Rendre le score de la balle
                counter_text = font.render(
                    str(ball.circles_destroyed), True, ball_colors[i]
                )
                counter_rect = counter_text.get_rect(
                    center=(rect_x + rect_width // 2 + 40 + shake_x, rect_y + rect_height // 2 + shake_y)
                )

                # Afficher le texte, le ":" et le score dans le rectangle
                screen.blit(text, text_rect)
                screen.blit(colon_text, colon_rect)
                screen.blit(counter_text, counter_rect)

    pygame.display.update()

pygame.quit()
