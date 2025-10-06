import pygame

class BaseGame:
    def __init__(self, screen):
        self.screen = screen
        self.running = True

    def update(self, gesture):
        """Update game state based on gesture input."""
        raise NotImplementedError

    def draw(self):
        """Render the game frame."""
        raise NotImplementedError

    def run(self, gesture_func):
        """Main loop that receives gestures from camera."""
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
            gesture = gesture_func()
            self.update(gesture)
            self.draw()
            pygame.display.flip()
            clock.tick(15)
