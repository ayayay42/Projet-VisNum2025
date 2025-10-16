import cv2
import pygame
from detection_mains.track_main import HandTracker
from utils.mouvements import get_direction_from_index
from jeux.snake import SnakeGame

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Snake")

font = pygame.font.Font(None, 48)
tracker = HandTracker()

def get_camera_data(cap):
    ret, frame = cap.read()
    if not ret:
        return None, None
    landmarks, frame = tracker.get_landmarks(frame)
    gesture = get_direction_from_index(landmarks)
    cv2.imshow("Hand Feed", frame)
    cv2.waitKey(1)
    return landmarks, gesture

def welcome_screen():
    screen.fill((30, 30, 30))
    title = font.render("Bienvenue au jeu du serpent", True, (255, 255, 255))
    subtitle = font.render("Pointe l'index vers la droite pour commencer", True, (0, 255, 0))
    screen.blit(title, (100, 200))
    screen.blit(subtitle, (80, 300))
    pygame.display.flip()

welcome_screen()

cap = cv2.VideoCapture(0)

# wait to start game
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            cap.release()
            cv2.destroyAllWindows()
            exit()
    landmarks, gesture = get_camera_data(cap)
    if gesture == "RIGHT":
        break

game = SnakeGame(screen)

# Game loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    landmarks, gesture = get_camera_data(cap)
    game.update(gesture)
    game.draw()

    if landmarks is not None:
        game.check_restart(landmarks)

    pygame.display.flip()
    clock.tick(30)

cap.release()
cv2.destroyAllWindows()
pygame.quit()
