import pygame
import random
import math

pygame.mixer.init()
destroy= pygame.mixer.Sound("sounds/nice.wav")
class Vaporization:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.particles = []
        self.create_particles()

    def create_particles(self):
        pygame.mixer.Sound.play(destroy)
        for _ in range(250):  # Augmenter le nombre de particules pour un effet dense
            angle = random.uniform(0, 2 * math.pi)  # Angle autour du cercle
            distance = random.uniform(
                self.radius * 0.9, self.radius * 1.1
            )  # Autour du périmètre
            size = random.randint(2, 5)  # Taille des particules
            self.particles.append(
                {
                    "x": self.x + distance * math.cos(angle),
                    "y": self.y + distance * math.sin(angle),
                    "vx": random.uniform(-0.5, 0.5),  # Oscillation légère
                    "vy": random.uniform(-0.5, 0.5),  # Oscillation légère
                    "radius": size,
                    "life": random.randint(30, 40),  # Durée de vie des particules
                    "color": (
                        max(0, min(255, self.color[0] + random.randint(-20, 20))),
                        max(0, min(255, self.color[1] + random.randint(-20, 20))),
                        max(0, min(255, self.color[2] + random.randint(-20, 20))),
                    ),
                }
            )

    def update(self):
        for particle in self.particles:
            # Oscillation légère autour de la position initiale
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["life"] -= 1
            particle["radius"] = max(0, particle["radius"] - 0.05)  # Rétrécissement
            particle["color"] = (
                max(0, particle["color"][0] - 5),  # Réduction progressive de la couleur
                max(0, particle["color"][1] - 5),
                max(0, particle["color"][2] - 5),
            )

    def draw(self, screen):
        for particle in self.particles:
            if particle["life"] > 0 and particle["radius"] > 0:
                pygame.draw.circle(
                    screen,
                    particle["color"],
                    (int(particle["x"]), int(particle["y"])),
                    int(particle["radius"]),
                )

    def is_done(self):
        return all(p["life"] <= 0 for p in self.particles)
