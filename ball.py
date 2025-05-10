import pygame


class Ball:
    def __init__(self, x, y, radius, color, border_color=None, border_radius=None):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.radius = radius
        self.color = color
        self.border_color = border_color
        self.border_radius = border_radius
        self.velocity_x = 5
        self.velocity_y = 5
        self.gravity = 0.5
        self.bounce_factor = 1.27
        self.max_speed = 13
        self.trail_positions = []
        self.max_trail_length = 15

    def update(self, screen_width, screen_height):
        # Appliquer la gravité
        self.velocity_y += self.gravity

        # Mettre à jour la position
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Gérer les collisions avec les bords
        # Rebond sur les bords horizontaux
        if self.x - self.radius < 0:
            self.x = self.radius
            self.velocity_x = -self.velocity_x * self.bounce_factor
        elif self.x + self.radius > screen_width:
            self.x = screen_width - self.radius
            self.velocity_x = -self.velocity_x * self.bounce_factor

        # Rebond sur les bords verticaux
        if self.y - self.radius < 0:
            self.y = self.radius
            self.velocity_y = -self.velocity_y * self.bounce_factor
        elif self.y + self.radius > screen_height:
            self.y = screen_height - self.radius
            self.velocity_y = -self.velocity_y * self.bounce_factor

    def draw(self, screen):
        # Dessiner la traînée
        for i, (pos_x, pos_y) in enumerate(self.trail_positions):
            # Calculer l'alpha (transparence) en fonction de l'âge de la position
            alpha = int(255 * (i / len(self.trail_positions)))
            trail_color = (0,0,255, alpha)  # Couleur de la traînée avec transparence
            
            # Dessiner chaque point de la traînée
            trail_radius = max(1, int(self.radius * (i / len(self.trail_positions))))
            pygame.draw.circle(screen, trail_color, [int(pos_x), int(pos_y)], trail_radius)

        # Dessiner la boule principale
        if self.border_color and self.border_radius:
            pygame.draw.circle(
                screen,
                self.border_color,
                [int(self.x), int(self.y)],
                self.border_radius,
            )
        pygame.draw.circle(screen, self.color, [int(self.x), int(self.y)], self.radius)
