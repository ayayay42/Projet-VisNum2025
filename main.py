import cv2
import pygame
import numpy as np
from hand_detection.hand_tracker import HandTracker
from utils.movements import get_direction_from_index, hand_present
from utils.leaderboard import Leaderboard
from games.snake import SnakeGame
from utils.evaluator import Evaluator

pygame.init()
screen = pygame.display.set_mode((1200, 600))
pygame.display.set_caption("Snake")

font = pygame.font.Font(None, 48)
tracker = HandTracker()

def get_real_gesture_from_keyboard():
    """Return the gesture the user indicates via the keyboard arrows."""
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        return "LEFT"
    if keys[pygame.K_RIGHT]:
        return "RIGHT"
    if keys[pygame.K_UP]:
        return "UP"
    if keys[pygame.K_DOWN]:
        return "DOWN"

    return "NONE"


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

    input_text = ""
    input_active = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                exit()
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_RETURN:
                    input_active = False
                else:
                    # append printable character
                    if event.unicode.isprintable():
                        input_text += event.unicode

        landmarks, gesture, cam_surf = get_camera_data(cap, cam_size)

        screen.fill((30, 30, 30))

        if input_active:
            prompt = font.render("Entrez votre nom puis appuyez sur Entrée :", True, (255, 255, 255))
            input_box_font = pygame.font.Font(None, 56)
            input_surf = input_box_font.render(input_text or "_", True, (255, 255, 255))

            screen.blit(prompt, (100, 160))
            pygame.draw.rect(screen, (50, 50, 50), (100, 220, 600, 70))
            screen.blit(input_surf, (110, 230))

            # preview camera while typing
            if cam_surf:
                screen.blit(cam_surf, (820, 20))

            pygame.display.flip()
            clock.tick(30)
            continue

        title = font.render(f"Bienvenue au jeu du serpent, {input_text}", True, (255, 255, 255))
        subtitle = font.render("Pointez l'index vers la droite pour commencer", True, (0, 255, 0))
        screen.blit(title, (100, 200))
        screen.blit(subtitle, (100, 300))

        if cam_surf:
            screen.blit(cam_surf, (820, 20))

        pygame.display.flip()
        clock.tick(30)

        if gesture == "RIGHT":
            return input_text

def render_wrapped_text(text, font, color, max_width, line_spacing=4):
    """
    Return a surface containing the wrapped text.
    - text: string (can contain spaces)
    - font: pygame Font object
    - color: (r,g,b)
    - max_width: max pixel width of the resulting surface
    """
    words = text.split()
    if not words:
        return None

    lines = []
    current = words[0]
    for w in words[1:]:
        test = current + " " + w
        test_w, _ = font.size(test)
        if test_w <= max_width:
            current = test
        else:
            lines.append(current)
            current = w
    lines.append(current)

    rendered_lines = [font.render(line, True, color) for line in lines]
    widths = [surf.get_width() for surf in rendered_lines]
    heights = [surf.get_height() for surf in rendered_lines]
    surf_w = max(widths)
    surf_h = sum(heights) + (len(heights)-1) * line_spacing

    surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
    y = 0
    for r in rendered_lines:
        surf.blit(r, (0, y))
        y += r.get_height() + line_spacing
    return surf

cap = cv2.VideoCapture(0)

player_name = welcome_screen(cap)

game = SnakeGame(screen)
evaluator = Evaluator()
lb = Leaderboard()

# Game loop
clock = pygame.time.Clock()
running = True
pause = False
cam_size = (360, 240)

NO_HAND_FRAMES_TO_PAUSE = 5    # require 5 consecutive frames with no hand to pause
HAND_FRAMES_TO_RESUME = 3      # require 3 consecutive frames with a hand to resume
no_hand_counter = 0
hand_counter = 0

font_pause = pygame.font.SysFont(None, 80)

PAUSE_TEXT_MAX_WIDTH = screen.get_width() - 200

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    landmarks, gesture, cam_surf = get_camera_data(cap, cam_size)
    real_gesture = get_real_gesture_from_keyboard()
    game.set_camera_surface(cam_surf)

    if not game.game_over:
        is_hand = hand_present(landmarks)

        if not is_hand:
            no_hand_counter += 1
            hand_counter = 0
        else:
            hand_counter += 1
            no_hand_counter = 0

        if no_hand_counter >= NO_HAND_FRAMES_TO_PAUSE and not pause:
            pause = True
            gesture = None  # prevent last gesture from persisting

        if hand_counter >= HAND_FRAMES_TO_RESUME and pause:
            pause = False

    else:
        # Reset counters when game is over
        no_hand_counter = 0
        hand_counter = 0
        pause = False

    evaluator.log_frame(
        hand_detected=is_hand,
        gesture_detected=gesture if gesture is not None else "NONE",
        gesture_real=real_gesture,
        paused=pause,
        game_over=game.game_over
    )

    if pause:
        game.draw()

        s = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        s.fill((0, 0, 0, 120))
        screen.blit(s, (0, 0))

        pause_message = "⏸ En pause — aucune main détectée"
        text_surf = render_wrapped_text(pause_message, font_pause, (255, 220, 0), PAUSE_TEXT_MAX_WIDTH)

        if text_surf:
            text_rect = text_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(text_surf, text_rect)

        pygame.display.flip()
        clock.tick(15)
        continue

    game.update(gesture)
    game.draw()

    # add score once when game becomes over
    if game.game_over and not prev_game_over_state:
        player = player_name if player_name else "Anonymous"
        score = max(0, len(game.snake) - 4)
        lb.add(player, score)

    # update persistent previous state
    prev_game_over_state = game.game_over

    if landmarks is not None:
        prev_game_over = game.game_over
        game.check_restart(landmarks)
        if prev_game_over and not game.game_over:
            no_hand_counter = 0
            hand_counter = 0
            pause = False

    pygame.display.flip()
    clock.tick(30)

cap.release()
cv2.destroyAllWindows()
pygame.quit()
