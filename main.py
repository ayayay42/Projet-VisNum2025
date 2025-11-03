import cv2
import pygame
import numpy as np
from hand_detection.hand_tracker import HandTracker
from utils.movements import get_direction_from_index
from games.snake import SnakeGame

pygame.init()
screen = pygame.display.set_mode((1200, 600))
pygame.display.set_caption("Snake")

font = pygame.font.Font(None, 48)
tracker = HandTracker()


def frame_to_surface(frame, size=None):
    if frame is None:
        return None
    if size is not None:
        frame = cv2.resize(frame, size)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w = frame_rgb.shape[:2]
    return pygame.image.frombuffer(frame_rgb.tobytes(), (w, h), "RGB")


def get_camera_data(cap, cam_size=(360, 240)):
    ret, frame = cap.read()
    if not ret:
        return None, None, None
    landmarks, frame = tracker.get_landmarks(frame)
    gesture = get_direction_from_index(landmarks)
    cam_surf = frame_to_surface(frame, size=cam_size)
    return landmarks, gesture, cam_surf


def welcome_screen(cap, cam_size=(360, 240)):
    """Show welcome screen and preview camera until gesture RIGHT is detected.
    Returns when gesture == 'RIGHT' or exits on quit.
    """
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                exit()

        landmarks, gesture, cam_surf = get_camera_data(cap, cam_size)

        screen.fill((30, 30, 30))
        title = font.render("Bienvenue au jeu du serpent", True, (255, 255, 255))
        subtitle = font.render("Pointe l'index vers la droite pour commencer", True, (0, 255, 0))
        screen.blit(title, (100, 200))
        screen.blit(subtitle, (100, 300))

        if cam_surf:
            screen.blit(cam_surf, (820, 20))

        pygame.display.flip()
        clock.tick(30)

        if gesture == "RIGHT":
            return


cap = cv2.VideoCapture(0)

# wait to start game (welcome screen handles camera preview and input)
welcome_screen(cap)

game = SnakeGame(screen)

# Game loop
clock = pygame.time.Clock()
running = True
cam_size = (360, 240)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    landmarks, gesture, cam_surf = get_camera_data(cap, cam_size)

    game.set_camera_surface(cam_surf)
    game.update(gesture)
    game.draw()

    if landmarks is not None:
        game.check_restart(landmarks)

    pygame.display.flip()
    clock.tick(30)

cap.release()
cv2.destroyAllWindows()
pygame.quit()
