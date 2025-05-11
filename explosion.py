import pygame
import random
import math
from vaporization import Vaporization  # noqa: F401


class Explosion:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.initial_radius = radius
        self.radius = radius // 2  # Commence plus petit
        self.color = color
        self.max_radius = radius * 5  # Grossit plus
        self.growth_rate = radius * 0.1  # Taux de croissance proportionnel
        self.alpha = 255
        self.fade_rate = 5  # Plus lent
        self.particles = []
        self.create_particles()

    def create_particles(self):
        # Plus de particules, plus visibles
        for _ in range(40):  # Augmenté de 20 à 40
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)  # Plus rapides
            size = random.randint(3, 8)  # Plus grosses
            self.particles.append(
                {
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "radius": size,
                    "life": random.randint(30, 60),  # Plus longue durée
                    "color": (
                        min(255, self.color[0] + random.randint(50, 100)),
                        min(255, self.color[1] + random.randint(50, 100)),
                        min(255, self.color[2] + random.randint(50, 100)),
                    ),  # Couleurs plus claires
                }
            )

    def update(self):
        # Croissance jusqu'au max_radius puis rétrécissement
        if self.radius < self.max_radius:
            self.radius += self.growth_rate
        else:
            self.radius = max(0, self.radius - self.growth_rate * 0.5)

        self.alpha = max(0, self.alpha - self.fade_rate)

        for particle in self.particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["life"] -= 1
            # Les particules rétrécissent avec le temps
            particle["radius"] = max(0, particle["radius"] - 0.1)

    def draw(self, screen):
        # Dessine le cercle principal avec effet de pulsation
        if self.alpha > 0 and self.radius > 0:
            s = pygame.Surface(
                (self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA
            )
            # Cercle extérieur
            pygame.draw.circle(
                s,
                (*self.color, self.alpha // 2),
                (self.max_radius, self.max_radius),
                self.radius,
                3,
            )
            # Cercle intérieur plus clair
            inner_radius = max(0, self.radius * 0.7)
            pygame.draw.circle(
                s,
                (
                    min(255, self.color[0] + 50),
                    min(255, self.color[1] + 50),
                    min(255, self.color[2] + 50),
                    self.alpha,
                ),
                (self.max_radius, self.max_radius),
                inner_radius,
                2,
            )
            screen.blit(s, (self.x - self.max_radius, self.y - self.max_radius))

        # Dessine les particules
        for particle in self.particles:
            if particle["life"] > 0 and particle["radius"] > 0:
                pygame.draw.circle(
                    screen,
                    particle["color"],
                    (int(particle["x"]), int(particle["y"])),
                    int(particle["radius"]),
                )

    def is_done(self):
        return self.alpha <= 0 and all(p["life"] <= 0 for p in self.particles)
