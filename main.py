import pygame
from ball import Ball
from circle import Circle
from explosion import Explosion, Vaporization
import random
from colors import colors
import argparse
import math
import pretty_midi
import time
import numpy

from scipy.signal import butter, lfilter


pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)

pygame.mixer.init()
pygame.mixer.music.set_volume(0.2)
MAX_CONCURRENT_NOTES = 8
SAMPLE_RATE = 44100
MAX_AMPLITUDE = 6000
pygame.mixer.set_num_channels(MAX_CONCURRENT_NOTES + 2)  # +2 pour la marge
midi_file = "sounds/test2.mid"  # Changez le chemin si nécessaire
midi_data = pretty_midi.PrettyMIDI(midi_file)
all_notes = [note for instrument in midi_data.instruments for note in instrument.notes]
all_notes.sort(key=lambda note: note.start)
note_index = 0
played_notes = []  # Pour enregistrer les notes jouées
MIN_TIME_BETWEEN_NOTES = 0.2  # Temps minimum entre deux notes (en secondes)


# Au début du code, initialiser le mixer avec un buffer plus grand
def lowpass_filter(data, cutoff=3000, fs=SAMPLE_RATE, order=6):
    nyq = 0.5 * fs
    norm_cutoff = cutoff / nyq
    b, a = butter(order, norm_cutoff, btype="low", analog=False)
    return lfilter(b, a, data)


# Modifier la fonction play_midi_note pour réutiliser les canaux audio
def play_midi_note(pitch, velocity=100, duration=0.2):
    try:
        duration = min(0.3, max(0.05, duration))
        frequency = 440 * (2 ** ((pitch - 69) / 12))
        n_samples = int(SAMPLE_RATE * duration)
        t = numpy.linspace(0, duration, n_samples, False)

        # Enveloppe ADSR
        attack_time = int(0.05 * n_samples)
        release_time = int(0.5 * n_samples)
        sustain_time = n_samples - attack_time - release_time

        envelope = numpy.ones(n_samples)
        envelope[:attack_time] = numpy.linspace(0, 1, attack_time)
        envelope[attack_time : attack_time + sustain_time] = 0.8
        envelope[-release_time:] = numpy.linspace(0.8, 0, release_time)

        # Onde fondamentale + harmoniques
        wave = numpy.sin(2 * numpy.pi * frequency * t)
        wave += 0.2 * numpy.sin(2 * 2 * numpy.pi * frequency * t)
        wave += 0.05 * numpy.sin(3 * 2 * numpy.pi * frequency * t)

        # Appliquer filtre passe-bas pour adoucir
        wave = lowpass_filter(wave)

        # Appliquer l'enveloppe
        wave *= envelope

        # Normaliser
        wave = wave / max(numpy.max(numpy.abs(wave)), 1e-6)
        amplitude = MAX_AMPLITUDE * (velocity / 127) * 0.8
        wave *= amplitude
        wave = numpy.clip(wave, -32767, 32767)

        # Stéréo identique L/R
        buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
        buf[:, 0] = wave.astype(numpy.int16)
        buf[:, 1] = buf[:, 0]

        sound = pygame.sndarray.make_sound(buf)
        channel = pygame.mixer.find_channel()
        if not channel:
            return False

        channel.play(sound)
        channel.fadeout(int(duration * 1000))  # Fondu en douceur
        return True

    except Exception as e:
        print(f"Erreur lors de la génération du son : {e}")
        return False


def clean_channels():
    """Libère les canaux audio qui ont fini de jouer"""
    for i in range(pygame.mixer.get_num_channels()):
        channel = pygame.mixer.Channel(i)
        if not channel.get_busy():
            channel.stop()


def play_bounce_note(ball):
    """Joue une note lors d'un rebond"""
    global note_index, played_notes

    if note_index < len(all_notes):
        note = all_notes[note_index]

        # Calculer la vélocité en fonction de la vitesse de la balle
        velocity = min(127, int(abs(ball.velocity_x + ball.velocity_y) * 10))

        # Enregistrer la note jouée
        played_notes.append((time.time(), note.pitch, velocity))

        # Jouer la note
        if play_midi_note(note.pitch, velocity):
            note_index += 1
            if note_index >= len(all_notes):
                note_index = 0  # Boucler au début si nécessaire


last_note_time = 0
note_delay = 0  # Temps entre les notes du fichier MIDI


def play_next_note():
    """Joue la prochaine note du fichier MIDI avec gestion améliorée"""
    global note_index

    # Nettoyer les canaux inactifs
    clean_channels()

    # Vérifier les canaux disponibles
    active_channels = sum(
        1
        for i in range(pygame.mixer.get_num_channels())
        if pygame.mixer.Channel(i).get_busy()
    )

    if active_channels < MAX_CONCURRENT_NOTES:
        if note_index < len(all_notes):
            note = all_notes[note_index]

            # Ajuster la durée pour éviter les notes trop longues
            note_duration = min(0.5, note.end - note.start)

            # Jouer la note avec un volume réduit si trop de canaux actifs
            velocity = note.velocity
            if active_channels > MAX_CONCURRENT_NOTES * 0.7:
                velocity = int(velocity * 0.8)

            if play_midi_note(note.pitch, velocity, note_duration):
                note_index += 1
                if note_index >= len(all_notes):
                    note_index = 0


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
    """Vérifie si deux balles se heurtent (version optimisée)."""
    dx = ball1.x - ball2.x
    dy = ball1.y - ball2.y
    distance_sq = dx * dx + dy * dy
    min_distance = ball1.radius + ball2.radius
    return distance_sq < (min_distance * min_distance)


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
    ball = Ball(
        position_ball_x + x_offset,
        position_ball_y,
        radius_ball,
        ball_color,
        random.uniform(-5, 5),
        random.uniform(-5, 5),
        border_color_ball,
        radius_ball + 2,
        text=text,
    )
    ball.last_bounce_time = 0  # Ajouter un suivi du dernier rebond
    return ball


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
    start_radius = 200
    number_of_circles = 50
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
next_circle_index = 15
circles_to_remove = []

base_circle = circles[0]
base_circle.min_radius = 100
base_circle.shrink_rate = 0.1

explosions = []

start_time = pygame.time.get_ticks()  # Temps de départ en millisecondes
for i in range(TOTAL_FRAMES):
    current_time = time.time()
    screen.fill((0, 0, 0))
    clock.tick(60)  # Limiter à 60 FPS
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
            if current_time - ball.last_bounce_time > MIN_TIME_BETWEEN_NOTES:
                play_next_note()  # Jouer la note suivante du fichier
                ball.last_bounce_time = current_time

        # Idem pour les collisions verticales
        if ball.y - ball.radius < 0 or ball.y + ball.radius > screen.get_height():
            if current_time - ball.last_bounce_time > MIN_TIME_BETWEEN_NOTES:
                play_next_note()  # Jouer la note suivante du fichier
                ball.last_bounce_time = current_time

        # Vérifier les collisions avec les cercles
        for circle in circles[:]:
            should_destroy, has_collided = circle.check_collision(ball)

            if should_destroy:
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

            elif (
                has_collided
                and current_time - ball.last_bounce_time > MIN_TIME_BETWEEN_NOTES
            ):
                # Jouer une note seulement quand il y a collision sans destruction
                play_next_note()
                ball.last_bounce_time = current_time

    # Mettez à jour et dessinez les explosions
    for explosion in explosions[:]:
        explosion.update()
        explosion.draw(screen)
        if explosion.is_done():
            explosions.remove(explosion)

    # Gérer les bords de l'écran

    # Collision avec les bords horizontaux
    if ball.x - ball.radius < 0 or ball.x + ball.radius > screen.get_width():
        if current_time - ball.last_bounce_time > MIN_TIME_BETWEEN_NOTES:
            play_next_note()  # Jouer la note suivante du fichier
            ball.last_bounce_time = current_time

    # Idem pour les collisions verticales
    if ball.y - ball.radius < 0 or ball.y + ball.radius > screen.get_height():
        if current_time - ball.last_bounce_time > MIN_TIME_BETWEEN_NOTES:
            play_next_note()  # Jouer la note suivante du fichier
            ball.last_bounce_time = current_time

    # Collision entre balles
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            if check_ball_collision(balls[i], balls[j]):
                resolve_ball_collision(balls[i], balls[j])
                if current_time - balls[i].last_bounce_time > MIN_TIME_BETWEEN_NOTES:
                    play_bounce_note(balls[i])
                    balls[i].last_bounce_time = current_time

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
                    center=(
                        rect_x + rect_width // 2 - 20 + shake_x,
                        rect_y + rect_height // 2 + shake_y,
                    )
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
                    center=(
                        rect_x + rect_width // 2 + 40 + shake_x,
                        rect_y + rect_height // 2 + shake_y,
                    )
                )

                # Afficher le texte, le ":" et le score dans le rectangle
                screen.blit(text, text_rect)
                screen.blit(colon_text, colon_rect)
                screen.blit(counter_text, counter_rect)
    if i % 10 == 0:  # Nettoyer tous les 10 frames
        clean_channels()
    pygame.display.update()


def save_played_notes(filename="played_notes.txt"):
    with open(filename, "w") as f:
        for t, pitch, velocity in played_notes:
            f.write(f"{t:.2f}, {pitch}, {velocity}\n")


# Avant pygame.quit(), sauvegardez les notes
save_played_notes()
pygame.quit()
