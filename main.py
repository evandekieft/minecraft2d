import pygame
import sys
from pygame.locals import QUIT, KEYDOWN, KEYUP
from constants import WINDOW_SIZE, GRID_SIZE, BLACK, WHITE
from world import Game

# Initialize PyGame
pygame.init()

# Set up the display
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Minecraft2D")


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
