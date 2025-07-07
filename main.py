import pygame
import sys
from pygame.locals import (
    QUIT, KEYDOWN, KEYUP, K_LEFT, K_RIGHT, K_UP, K_DOWN
)

# Initialize PyGame
pygame.init()

# Constants
WINDOW_SIZE = (800, 600)
GRID_SIZE = 32  # Size of each grid cell in pixels
GRID_WIDTH = WINDOW_SIZE[0] // GRID_SIZE
GRID_HEIGHT = WINDOW_SIZE[1] // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)

# Set up the display
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Minecraft2D")

clock = pygame.time.Clock()

class Player:
    def __init__(self):
        self.grid_x = GRID_WIDTH // 2
        self.grid_y = GRID_HEIGHT // 2
        self.color = BLUE
        self.move_delay = 0.2  # seconds between moves
        self.move_timer = 0
        self.last_key = None
        self.moved = False  # Tracks if we've moved on this key press

    def handle_keydown(self, key):
        if key in (K_LEFT, K_RIGHT, K_UP, K_DOWN):
            if key != self.last_key:
                self.moved = False
            self.last_key = key
            
            # Immediate move on first key press
            if not self.moved:
                self._move_from_key(key)
                self.moved = True
                self.move_timer = 0  # Reset timer on new key press

    def handle_keyup(self, key):
        if key == self.last_key:
            self.last_key = None
            self.moved = False

    def update(self, dt):
        if self.last_key is not None:
            self.move_timer += dt
            if self.move_timer >= self.move_delay:
                self._move_from_key(self.last_key)
                self.move_timer = 0

    def _move_from_key(self, key):
        dx, dy = 0, 0
        if key == K_LEFT:
            dx = -1
        elif key == K_RIGHT:
            dx = 1
        elif key == K_UP:
            dy = -1
        elif key == K_DOWN:
            dy = 1
            
        if dx != 0 or dy != 0:
            self.move(dx, dy)

    def move(self, dx, dy):
        self.grid_x = max(0, min(GRID_WIDTH - 1, self.grid_x + dx))
        self.grid_y = max(0, min(GRID_HEIGHT - 1, self.grid_y + dy))

class Game:
    def __init__(self):
        self.player = Player()
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Initialize world with some blocks
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                # Add some ground blocks
                if y >= GRID_HEIGHT - 2:
                    self.grid[y][x] = 1  # Ground block

def draw_block(x, y, type):
    rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    if type == 0:  # Air
        pygame.draw.rect(screen, WHITE, rect, 1)
    elif type == 1:  # Ground
        pygame.draw.rect(screen, BROWN, rect)

def main():
    game = Game()
    clock = pygame.time.Clock()
    
    while True:
        dt = clock.tick(60) / 1000.0  # Convert to seconds
        
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                game.player.handle_keydown(event.key)
            elif event.type == KEYUP:
                game.player.handle_keyup(event.key)

        # Update game state
        game.player.update(dt)

        # Drawing
        screen.fill(BLACK)
        
        # Draw world
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                draw_block(x, y, game.grid[y][x])
        
        # Draw player
        player_rect = pygame.Rect(
            game.player.grid_x * GRID_SIZE + 2,
            game.player.grid_y * GRID_SIZE + 2,
            GRID_SIZE - 4,
            GRID_SIZE - 4
        )
        pygame.draw.rect(screen, game.player.color, player_rect)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
