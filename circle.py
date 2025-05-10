import pygame
import math


class Circle:
    def __init__(
        self,
        x,
        y,
        radius,
        color,
        border_width=0,
        hole_radius=0,
        gap_angle=0,  # Angle (en radians) où commencer le trou dans le contour
        gap_size=0,  # Taille du trou (en radians)
    ):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.border_width = border_width
        self.angle = 0
        self.hole_radius = hole_radius
        self.gap_angle = gap_angle  # Position du trou dans le contour
        self.gap_size = gap_size  # Taille du trou
        self.rotation_speed = 0.02  # Vitesse de rotation en radians par frame
        self.min_radius = 100  # Tu peux ajuster cette valeur
        self.shrink_rate = 0.5  # Diminution du rayon à chaque frame

    def draw(self, screen):
        num_points = 60  # Nombre de points pour dessiner le cercle

        # Dessiner le cercle extérieur avec un trou
        outer_points = []
        for i in range(num_points + 1):
            angle = self.angle + (2 * math.pi * i / num_points)

            # Vérifier si cet angle est dans la zone du trou
            if not (
                self.gap_size > 0
                and (angle - self.angle) % (2 * math.pi) > self.gap_angle
                and (angle - self.angle) % (2 * math.pi)
                < self.gap_angle + self.gap_size
            ):
                px = self.x + self.radius * math.cos(angle)
                py = self.y + self.radius * math.sin(angle)
                outer_points.append((px, py))
            elif outer_points:  # Si on rencontre le trou et qu'il y a des points
                if len(outer_points) > 1:
                    pygame.draw.lines(
                        screen, self.color, False, outer_points, self.border_width
                    )
                outer_points = []

        # Dessiner les segments restants
        if len(outer_points) > 1:
            pygame.draw.lines(
                screen, self.color, False, outer_points, self.border_width
            )

        self.angle += self.rotation_speed

    def check_collision(self, ball):
        # Calculer la distance entre les centres
        dx = ball.x - self.x
        dy = ball.y - self.y
        distance_sq = dx * dx + dy * dy
        effective_radius = self.radius - ball.radius

        # Optimisation
        if not (
            (effective_radius * 0.9) ** 2
            < distance_sq
            < (self.radius + ball.radius) ** 2
        ):
            return False

        distance = math.sqrt(distance_sq)

        angle = math.atan2(dy, dx) % (2 * math.pi)
        relative_angle = (angle - self.angle) % (2 * math.pi)
        gap_start = self.gap_angle
        gap_end = (gap_start + self.gap_size) % (2 * math.pi)

        in_gap = False
        if gap_start < gap_end:
            in_gap = gap_start <= relative_angle <= gap_end
        else:
            in_gap = relative_angle >= gap_start or relative_angle <= gap_end

        # === DESTRUCTION SI DANS LE TROU ===
        if in_gap and distance > (self.radius - ball.radius * 1.8):
            return True

        # Vérifier la collision avec le cercle extérieur
        if abs(distance - self.radius) < ball.radius * 1.1:
            # Calculer la position précédente relative
            prev_dx = ball.prev_x - self.x
            prev_dy = ball.prev_y - self.y
            prev_distance = math.sqrt(prev_dx * prev_dx + prev_dy * prev_dy)

            # Vecteur normal (toujours pointant vers l'extérieur)
            nx = dx / distance
            ny = dy / distance

            # Détection de traversée de paroi
            if (prev_distance < self.radius and distance >= self.radius) or (
                prev_distance > self.radius and distance <= self.radius
            ):
                # Calcul précis du point de collision
                t = (self.radius - prev_distance) / (distance - prev_distance)
                collision_x = ball.prev_x + t * (ball.x - ball.prev_x)
                collision_y = ball.prev_y + t * (ball.y - ball.prev_y)

                # Recalculer le vecteur normal
                col_dx = collision_x - self.x
                col_dy = collision_y - self.y
                col_dist = math.sqrt(col_dx * col_dx + col_dy * col_dy)
                nx = col_dx / col_dist
                ny = col_dy / col_dist

            # Repositionnement précis avec marge de sécurité
            if distance < self.radius:
                ball.x = self.x + nx * (self.radius - ball.radius * 0.95)
                ball.y = self.y + ny * (self.radius - ball.radius * 0.95)
            else:
                ball.x = self.x + nx * (self.radius + ball.radius * 0.95)
                ball.y = self.y + ny * (self.radius + ball.radius * 0.95)

            # Calcul du rebond
            dot_product = ball.velocity_x * nx + ball.velocity_y * ny
            ball.velocity_x = (
                ball.velocity_x - 2 * dot_product * nx
            ) * ball.bounce_factor
            ball.velocity_y = (
                ball.velocity_y - 2 * dot_product * ny
            ) * ball.bounce_factor

        # Mise à jour de la position précédente
        ball.prev_x = ball.x
        ball.prev_y = ball.y

        speed = math.sqrt(ball.velocity_x**2 + ball.velocity_y**2)
        if speed > ball.max_speed:
            ball.velocity_x = ball.velocity_x / speed * ball.max_speed
            ball.velocity_y = ball.velocity_y / speed * ball.max_speed
        return False
