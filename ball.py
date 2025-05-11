import pygame


class Ball:
    def __init__(self, x, y, radius, color, velocity_x, velocity_y, border_color=None, border_radius=None, text=""):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.radius = radius
        self.color = color
        self.border_color = border_color
        self.border_radius = border_radius
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.gravity = 0.5
        self.bounce_factor = 1.27
        self.max_speed = 13
        self.trail_positions = []
        self.max_trail_length = 15
        self.text = text
        self.circles_destroyed = 0

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
            alpha = int(150 * (1 - i / len(self.trail_positions)))  # Transparence réduite pour un effet plus subtil
            trail_color = (*self.color[:3], alpha)  # Couleur de la traînée avec transparence

            # Calculer un rayon plus petit pour les cercles plus anciens
            trail_radius = max(1, int(self.radius * (1 - i / len(self.trail_positions) * 0.5)))

            # Dessiner directement sur l'écran avec transparence
            trail_surface = pygame.Surface((trail_radius * 2, trail_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, trail_color, (trail_radius, trail_radius), trail_radius)
            screen.blit(trail_surface, (int(pos_x - trail_radius), int(pos_y - trail_radius)))

        # Dessiner la boule principale
        if self.border_color and self.border_radius:
            pygame.draw.circle(
                screen,
                self.border_color,
                [int(self.x), int(self.y)],
                self.border_radius,
            )
        pygame.draw.circle(screen, self.color, [int(self.x), int(self.y)], self.radius)

        if self.text:
            font = pygame.font.Font(None, 24)  # Taille de la police
            text_surface = font.render(self.text, True, (0, 0, 0))  # Texte en blanc
            text_rect = text_surface.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(text_surface, text_rect)

        # font = pygame.font.Font(None, 20)
        # counter_text = font.render(f"{self.circles_destroyed}", True, (255, 255, 255))
        # screen.blit(counter_text, (int(self.x) - 10, int(self.y) - self.radius - 20))
