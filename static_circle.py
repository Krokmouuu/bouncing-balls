import pygame
import math

class StaticCircle:
    def __init__(self, x, y, radius, color, border_width=0, hole_radius=0):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.border_width = border_width
        self.angle = 0
        self.rotation_speed = 0.02  # Vitesse de rotation en radians par frame
        self.hole_radius = hole_radius  # Rayon du trou central

    def draw(self, screen):
        # Calculer les points du cercle extérieur en rotation
        outer_points = []
        num_points = 60  # Nombre de points pour dessiner le cercle
        for i in range(num_points):
            angle = self.angle + (2 * math.pi * i / num_points)
            px = self.x + self.radius * math.cos(angle)
            py = self.y + self.radius * math.sin(angle)
            outer_points.append((px, py))
        
        # Calculer les points du trou intérieur en rotation
        inner_points = []
        for i in range(num_points):
            angle = self.angle + (2 * math.pi * i / num_points)
            px = self.x + self.hole_radius * math.cos(angle)
            py = self.y + self.hole_radius * math.sin(angle)
            inner_points.append((px, py))
        
        # Dessiner le cercle extérieur
        if len(outer_points) > 2:
            pygame.draw.lines(screen, self.color, True, outer_points, self.border_width)
        
        # Dessiner le trou intérieur
        if len(inner_points) > 2:
            pygame.draw.lines(screen, (0, 0, 0), True, inner_points, self.border_width)
        
        # Mettre à jour l'angle pour la prochaine frame
        self.angle += self.rotation_speed

    def check_collision(self, ball):
        # Calculer la distance entre les centres
        dx = ball.x - self.x
        dy = ball.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Vérifier si la balle touche le cercle (en tenant compte de la bordure)
        if distance > (self.radius - ball.radius) and distance < (self.radius + ball.radius):
            # Calculer le vecteur normal de collision
            nx = dx / distance
            ny = dy / distance
            
            # Calculer la nouvelle vélocité
            dot_product = ball.velocity_x * nx + ball.velocity_y * ny
            ball.velocity_x = (ball.velocity_x - 2 * dot_product * nx) * ball.bounce_factor
            ball.velocity_y = (ball.velocity_y - 2 * dot_product * ny) * ball.bounce_factor
            
            # Repositionner la balle pour éviter qu'elle ne reste coincée
            if distance < self.radius:
                # Si la balle est à l'intérieur, la repousser vers l'extérieur
                ball.x = self.x + nx * (self.radius - ball.radius)
                ball.y = self.y + ny * (self.radius - ball.radius)
            else:
                # Si la balle est à l'extérieur, la repousser vers l'intérieur
                ball.x = self.x + nx * (self.radius + ball.radius)
                ball.y = self.y + ny * (self.radius + ball.radius) 