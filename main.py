import pygame
import sys
import random
from pygame.locals import (
    QUIT, KEYDOWN, KEYUP, K_LEFT, K_RIGHT, K_UP, K_DOWN
)

# Initialize PyGame
pygame.init()

# Constants
WINDOW_SIZE = (800, 600)
GRID_SIZE = 16  # Size of each grid cell in pixels
GRID_WIDTH = WINDOW_SIZE[0] // GRID_SIZE
GRID_HEIGHT = WINDOW_SIZE[1] // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
DARK_BROWN = (101, 67, 33)

# Set up the display
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Minecraft2D")

clock = pygame.time.Clock()

class Camera:
    def __init__(self, smoothing=0.05):
        self.x = 0.0
        self.y = 0.0
        self.smoothing = smoothing
    
    def update(self, target_x, target_y, dt):
        # Calculate target camera position (center the player)
        target_camera_x = target_x
        target_camera_y = target_y
        
        # Smooth interpolation toward target (dt is available but not needed for frame-rate independent smoothing)
        self.x += (target_camera_x - self.x) * self.smoothing
        self.y += (target_camera_y - self.y) * self.smoothing
    
    def world_to_screen(self, world_x, world_y):
        # Convert world coordinates to screen coordinates
        screen_x = (world_x - self.x) * GRID_SIZE + WINDOW_SIZE[0] // 2
        screen_y = (world_y - self.y) * GRID_SIZE + WINDOW_SIZE[1] // 2
        return screen_x, screen_y
    
    def get_visible_bounds(self):
        # Calculate which world coordinates are visible
        half_screen_width = WINDOW_SIZE[0] // (2 * GRID_SIZE)
        half_screen_height = WINDOW_SIZE[1] // (2 * GRID_SIZE)
        
        left = int(self.x - half_screen_width - 1)
        right = int(self.x + half_screen_width + 1)
        top = int(self.y - half_screen_height - 1)
        bottom = int(self.y + half_screen_height + 1)
        
        return left, right, top, bottom

class Block:
    def __init__(self, block_type):
        self.type = block_type
        self.walkable = self._get_walkable(block_type)
        self.color = self._get_color(block_type)
    
    def _get_walkable(self, block_type):
        walkable_blocks = {"grass", "dirt", "water"}
        return block_type in walkable_blocks
    
    def _get_color(self, block_type):
        colors = {
            "grass": GREEN,
            "tree": LIGHT_BROWN,
            "dirt": DARK_BROWN,
            "water": BLUE
        }
        return colors.get(block_type, WHITE)

class Player:
    def __init__(self):
        self.world_x = 0
        self.world_y = 0
        self.color = BLUE
        self.orientation = "north"  # north, south, east, west

    def handle_keydown(self, key):
        if key in (K_LEFT, K_RIGHT, K_UP, K_DOWN):
            if key == K_LEFT:
                self.orientation = "west"
            elif key == K_RIGHT:
                self.orientation = "east"
            elif key == K_UP:
                self.orientation = "north"
            elif key == K_DOWN:
                self.orientation = "south"

    def handle_keyup(self, key, game):
        if key in (K_LEFT, K_RIGHT, K_UP, K_DOWN):
            dx, dy = 0, 0
            if self.orientation == "west":
                dx = -1
            elif self.orientation == "east":
                dx = 1
            elif self.orientation == "north":
                dy = -1
            elif self.orientation == "south":
                dy = 1
            self.move(dx, dy, game)

    def update(self, dt):
        # Currently no per-frame updates needed for player
        pass

    def move(self, dx, dy, game):
        new_x = self.world_x + dx
        new_y = self.world_y + dy
        
        # Check if target block is walkable
        target_block = game.get_block(new_x, new_y)
        if target_block and target_block.walkable:
            self.world_x = new_x
            self.world_y = new_y

class Game:
    def __init__(self):
        self.player = Player()
        self.camera = Camera()
        self.chunks = {}  # Dict to store chunks by (chunk_x, chunk_y)
        self.chunk_size = 16  # Size of each chunk in blocks
        
        # Generate initial chunks around player
        self._generate_chunks_around_player()
    
    def _generate_chunks_around_player(self):
        # Generate chunks in a 3x3 area around player
        player_chunk_x = self.player.world_x // self.chunk_size
        player_chunk_y = self.player.world_y // self.chunk_size
        
        for cy in range(player_chunk_y - 1, player_chunk_y + 2):
            for cx in range(player_chunk_x - 1, player_chunk_x + 2):
                if (cx, cy) not in self.chunks:
                    self._generate_chunk(cx, cy)
    
    def _generate_chunk(self, chunk_x, chunk_y):
        # Generate a chunk at the given chunk coordinates
        chunk = {}
        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                world_x = chunk_x * self.chunk_size + x
                world_y = chunk_y * self.chunk_size + y
                
                # Use world coordinates for consistent random generation
                random.seed(world_x * 1000 + world_y)
                if random.random() < 0.9:
                    chunk[(x, y)] = Block("grass")
                else:
                    chunk[(x, y)] = Block("tree")
        
        self.chunks[(chunk_x, chunk_y)] = chunk
    
    def get_block(self, world_x, world_y):
        # Get block at world coordinates
        chunk_x = world_x // self.chunk_size
        chunk_y = world_y // self.chunk_size
        
        if (chunk_x, chunk_y) not in self.chunks:
            self._generate_chunk(chunk_x, chunk_y)
        
        chunk = self.chunks[(chunk_x, chunk_y)]
        local_x = world_x % self.chunk_size
        local_y = world_y % self.chunk_size
        
        return chunk.get((local_x, local_y))

def draw_block(screen_x, screen_y, block):
    rect = pygame.Rect(screen_x, screen_y, GRID_SIZE, GRID_SIZE)
    if block:
        pygame.draw.rect(screen, block.color, rect)
    else:
        pygame.draw.rect(screen, WHITE, rect, 1)

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
                game.player.handle_keyup(event.key, game)

        # Update game state
        game.player.update(dt)
        game.camera.update(game.player.world_x, game.player.world_y, dt)
        game._generate_chunks_around_player()  # Generate new chunks as needed

        # Drawing
        screen.fill(BLACK)
        
        # Draw world - only visible blocks
        left, right, top, bottom = game.camera.get_visible_bounds()
        
        for world_y in range(top, bottom + 1):
            for world_x in range(left, right + 1):
                block = game.get_block(world_x, world_y)
                if block:
                    screen_x, screen_y = game.camera.world_to_screen(world_x, world_y)
                    # Only draw if on screen
                    if -GRID_SIZE < screen_x < WINDOW_SIZE[0] and -GRID_SIZE < screen_y < WINDOW_SIZE[1]:
                        draw_block(screen_x, screen_y, block)
        
        # Draw player
        player_screen_x, player_screen_y = game.camera.world_to_screen(game.player.world_x, game.player.world_y)
        player_rect = pygame.Rect(
            player_screen_x + 2,
            player_screen_y + 2,
            GRID_SIZE - 4,
            GRID_SIZE - 4
        )
        pygame.draw.rect(screen, game.player.color, player_rect)
        
        # Draw orientation indicator
        center_x = player_screen_x + GRID_SIZE // 2
        center_y = player_screen_y + GRID_SIZE // 2
        arrow_length = 4
        
        if game.player.orientation == "north":
            end_x, end_y = center_x, center_y - arrow_length
        elif game.player.orientation == "south":
            end_x, end_y = center_x, center_y + arrow_length
        elif game.player.orientation == "east":
            end_x, end_y = center_x + arrow_length, center_y
        elif game.player.orientation == "west":
            end_x, end_y = center_x - arrow_length, center_y
            
        pygame.draw.line(screen, WHITE, (center_x, center_y), (end_x, end_y), 2)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
