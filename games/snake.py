import pygame
import random
from .base_game import BaseGame
from utils.movements import detect_open_hand
from utils.leaderboard import Leaderboard

def render_wrapped_text(text, font, color, max_width, line_spacing=4):
    """
    Return a surface containing the wrapped text.
    - text: string (can contain spaces and '\n' for paragraph breaks)
    - font: pygame Font object
    - color: (r,g,b)
    - max_width: max pixel width of the resulting surface
    """
    # Split by explicit newlines first to preserve paragraph breaks
    paragraphs = text.split('\n')
    if not paragraphs:
        return None

    lines = []
    for para in paragraphs:
        # If paragraph is empty, keep an empty line
        if not para:
            lines.append('')
            continue
        words = para.split()
        if not words:
            lines.append('')
            continue

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
    surf_w = max(widths) if widths else 0
    surf_h = sum(heights) + (len(heights)-1) * line_spacing if heights else 0

    surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
    y = 0
    for r in rendered_lines:
        surf.blit(r, (0, y))
        y += r.get_height() + line_spacing
    return surf



class SnakeGame(BaseGame):
    def __init__(self, screen):
        super().__init__(screen)
        self.cell_size = 20
        self.width, self.height = 800, 600
        self.cam_pos = (820, 20)
        self.cam_surf = None
        self.reset()

    def reset(self):
        self.snake = [(100, 100)]
        self.direction = (self.cell_size, 0)
        self.food = (200, 200)
        self.game_over = False
        self.move_delay = 6
        self.frame_count = 0
        head_x, head_y = 100, 100
        length = 4
        self.snake = [(head_x - i * self.cell_size, head_y) for i in range(length)]


    def update(self, gesture):
        if self.game_over:
            return

        if gesture == "LEFT" and self.direction != (self.cell_size, 0):
            self.direction = (-self.cell_size, 0)
        elif gesture == "RIGHT" and self.direction != (-self.cell_size, 0):
            self.direction = (self.cell_size, 0)
        elif gesture == "UP" and self.direction != (0, self.cell_size):
            self.direction = (0, -self.cell_size)
        elif gesture == "DOWN" and self.direction != (0, -self.cell_size):
            self.direction = (0, self.cell_size)

        self.frame_count += 1
        if self.frame_count < self.move_delay:
            return
        self.frame_count = 0

        head = (self.snake[0][0] + self.direction[0],
                self.snake[0][1] + self.direction[1])

        # Si touche le mur: fin du jeu
        if head[0] < 0 or head[0] >= self.width or head[1] < 0 or head[1] >= self.height:
            self.game_over = True
            return

        if head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, head)

        if head == self.food:
            self.food = (random.randrange(0, self.width, self.cell_size),
                         random.randrange(0, self.height, self.cell_size))
        else:
            self.snake.pop()

    def draw_grid(self):
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, (40, 40, 40), (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, (40, 40, 40), (0, y), (self.width, y))

    def draw(self):
        font = pygame.font.Font(None, 72)
        lb = Leaderboard()
        self.screen.fill((0, 0, 0))
        self.draw_grid()
        msg_score = font.render(f"Score: {len(self.snake) - 4}", True, (255, 255, 255))
        raw_leaderboard = lb.get_top(5)
        leaderboard_lines = [f"{i+1}. {entry['name']} - {entry['score']}" for i, entry in enumerate(raw_leaderboard)]
        leaderboard_text = "Classement:\n" + "\n".join(leaderboard_lines)
        msg_leaderboard = render_wrapped_text(leaderboard_text, pygame.font.Font(None, 36), (255, 255, 0), 300)
        self.screen.blit(msg_score, (820, 300))
        self.screen.blit(msg_leaderboard, (820, 360))

        if self.game_over:
            msg = font.render("FIN DU JEU", True, (255, 0, 0))
            sub_font = pygame.font.Font(None, 48)
            sub_msg = sub_font.render("Ouvrez votre main pour recommencer", True, (255, 255, 255))

            self.screen.blit(self.cam_surf, self.cam_pos)
            self.screen.blit(msg, (self.width // 4, self.height // 2 - 40))
            self.screen.blit(sub_msg, (self.width // 5, self.height // 2 + 20))
            pygame.display.flip()
            return

        for segment in self.snake:
            pygame.draw.rect(self.screen, (0, 255, 0), (*segment, self.cell_size, self.cell_size))

        pygame.draw.rect(self.screen, (255, 0, 0), (*self.food, self.cell_size, self.cell_size))
        self.screen.blit(self.cam_surf, self.cam_pos)

    def check_restart(self, landmarks):
        if self.game_over and detect_open_hand(landmarks):
            self.reset()

    def set_camera_surface(self, surf):
        """Set the camera surface to be blitted by the game on each draw call."""
        self.cam_surf = surf
