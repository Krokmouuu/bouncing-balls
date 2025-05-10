import pygame
from ball import Ball
from static_circle import StaticCircle

pygame.init()

screen = pygame.display.set_mode((1920, 1080))
screen.fill((0, 0, 0))

# Créer le cercle statique (plus petit) avec seulement le contour
static_circle = StaticCircle(700, 540, 400, (255, 255, 255), 5)  # Réduit l'épaisseur du contour à 5 pixels

def reset_ball():
    return Ball(540, 200, 40, (0, 0, 255), (255, 255, 255), 42)

# Créer une balle avec une vélocité initiale
ball = reset_ball()
ball.velocity_x = 0  # Vitesse horizontale initiale
ball.velocity_y = 0  # Vitesse verticale initiale

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:  # Appuyer sur R pour réinitialiser
            ball = reset_ball()
            ball.velocity_x = 0
            ball.velocity_y = 0
    screen.fill((0, 0, 0))
    
    # Dessiner le cercle statique
    static_circle.draw(screen)
    
    # Mettre à jour et dessiner la balle
    ball.update(screen.get_width(), screen.get_height())
    static_circle.check_collision(ball)  # Vérifier la collision avec le cercle statique
    ball.draw(screen)
    
    clock.tick(60)
    pygame.display.update()

pygame.quit()