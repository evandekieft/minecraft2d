import pygame
import sys
from pygame.locals import QUIT, KEYDOWN, KEYUP
from constants import WINDOW_SIZE, GRID_SIZE, BLACK, WHITE, GAME_HEIGHT, INVENTORY_HEIGHT
from world import Game

# Initialize PyGame
pygame.init()

# Set up the display
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Minecraft2D")


def draw_block(screen_x, screen_y, block, is_being_mined=False, mining_progress=0.0):
    rect = pygame.Rect(screen_x, screen_y, GRID_SIZE, GRID_SIZE)
    if block:
        color = block.color
        
        # Apply blinking effect if being mined
        if is_being_mined:
            # Blink faster as mining progresses
            blink_rate = 2.0 + mining_progress * 8.0  # 2-10 Hz
            blink_phase = pygame.time.get_ticks() / 1000.0 * blink_rate
            if int(blink_phase) % 2 == 0:
                # Darken the color during blink
                color = tuple(max(0, int(c * 0.4)) for c in color)
        
        pygame.draw.rect(screen, color, rect)
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
                game.player.handle_keydown(event.key, game)
            elif event.type == KEYUP:
                game.player.handle_keyup(event.key, game)

        # Update game state
        game.player.update(dt, game)
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
                    # Only draw if on screen (within game area)
                    if -GRID_SIZE < screen_x < WINDOW_SIZE[0] and -GRID_SIZE < screen_y < GAME_HEIGHT:
                        # Check if this block is being mined
                        is_being_mined = (game.player.is_mining and 
                                        game.player.mining_target == (world_x, world_y))
                        mining_progress = 0.0
                        if is_being_mined and block.minable:
                            mining_progress = 1.0 - (block.current_health / block.max_health)
                        
                        draw_block(screen_x, screen_y, block, is_being_mined, mining_progress)
        
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

        # Draw inventory
        draw_inventory(screen, game.player)

        pygame.display.flip()
        clock.tick(60)


def draw_inventory(screen, player):
    # Draw black inventory background
    inventory_rect = pygame.Rect(0, GAME_HEIGHT, WINDOW_SIZE[0], INVENTORY_HEIGHT)
    pygame.draw.rect(screen, BLACK, inventory_rect)
    
    # Get top 5 inventory items
    top_items = player.get_top_inventory_items(5)
    
    # Calculate slot dimensions and positions
    slot_size = 50
    slot_spacing = 10
    total_width = 5 * slot_size + 4 * slot_spacing
    start_x = (WINDOW_SIZE[0] - total_width) // 2
    start_y = GAME_HEIGHT + (INVENTORY_HEIGHT - slot_size) // 2
    
    # Draw 5 inventory slots
    for i in range(5):
        slot_x = start_x + i * (slot_size + slot_spacing)
        slot_y = start_y
        
        # Draw slot background
        slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
        pygame.draw.rect(screen, (64, 64, 64), slot_rect)  # Dark gray
        
        # Draw border (highlight active slot)
        border_color = WHITE if i == player.active_slot else (128, 128, 128)
        border_width = 3 if i == player.active_slot else 1
        pygame.draw.rect(screen, border_color, slot_rect, border_width)
        
        # Draw block if available
        if i < len(top_items):
            block_type, count = top_items[i]
            
            # Get block color (import from world to get Block class)
            from world import Block
            temp_block = Block(block_type)
            
            # Draw block color
            block_rect = pygame.Rect(slot_x + 5, slot_y + 5, slot_size - 10, slot_size - 30)
            pygame.draw.rect(screen, temp_block.color, block_rect)
            
            # Draw count text
            font = pygame.font.Font(None, 24)
            count_text = font.render(str(count), True, WHITE)
            text_x = slot_x + slot_size // 2 - count_text.get_width() // 2
            text_y = slot_y + slot_size - 20
            screen.blit(count_text, (text_x, text_y))

if __name__ == "__main__":
    main()
