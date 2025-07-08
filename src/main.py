import pygame
import sys
from pygame.locals import QUIT, KEYDOWN, KEYUP, K_ESCAPE, K_LEFTBRACKET, K_RIGHTBRACKET
from constants import (
    WINDOW_SIZE,
    GRID_SIZE,
    BLACK,
    WHITE,
    GAME_HEIGHT,
    INVENTORY_HEIGHT,
)
from menu import MenuSystem
from world_manager import WorldManager
from lighting import lighting_system

# Initialize PyGame
pygame.init()

# Set up the display
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Minecraft2D")


def draw_block(screen_x, screen_y, block, is_being_mined=False, mining_progress=0.0):
    rect = pygame.Rect(screen_x, screen_y, GRID_SIZE, GRID_SIZE)
    if block:
        # Draw the main block
        pygame.draw.rect(screen, block.color, rect)

        # Draw mining progress bar if being mined
        if is_being_mined and mining_progress > 0:
            # Calculate progress bar dimensions
            bar_height = max(2, GRID_SIZE // 10)  # At least 2 pixels high
            bar_width = int(GRID_SIZE * 0.8)  # 80% of block width
            bar_x = screen_x + (GRID_SIZE - bar_width) // 2
            bar_y = screen_y + GRID_SIZE - bar_height - 2  # 2px from bottom

            # Draw background of progress bar (empty part)
            pygame.draw.rect(
                screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height)
            )

            # Draw filled part of progress bar
            fill_width = int(bar_width * mining_progress)
            if fill_width > 0:
                # Color changes from red to green as progress increases
                red = int(255 * (1 - mining_progress))
                green = int(255 * mining_progress)
                pygame.draw.rect(
                    screen, (red, green, 0), (bar_x, bar_y, fill_width, bar_height)
                )
    else:
        # Draw empty block (air)
        pygame.draw.rect(screen, WHITE, rect, 1)


def main():
    clock = pygame.time.Clock()
    menu_system = MenuSystem(screen)
    world_manager = WorldManager()

    # Game state
    game = None
    game_state = "menu"  # "menu" or "playing" or "paused"
    current_world_name = None

    while True:
        dt = clock.tick(60) / 1000.0

        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                # Save before quitting if in game
                if game and current_world_name and game_state == "playing":
                    world_manager.save_world(game, current_world_name)
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN:
                if game_state == "menu":
                    # Handle menu input
                    action = menu_system.handle_event(event)
                    if action == "quit":
                        pygame.quit()
                        sys.exit()
                    elif isinstance(action, tuple):
                        action_type, data = action
                        if action_type == "load_world":
                            # Load existing world
                            game = world_manager.load_world(data)
                            if game:
                                current_world_name = data
                                game_state = "playing"
                                menu_system.reset_to_main_menu()
                        elif action_type == "create_world":
                            # Create new world
                            game = world_manager.create_new_world(data)
                            if game:
                                current_world_name = data
                                game_state = "playing"
                                menu_system.reset_to_main_menu()

                elif game_state == "playing":
                    if event.key == K_ESCAPE:
                        # Show pause menu
                        menu_system.show_pause_menu()
                        game_state = "paused"
                    elif event.key == K_LEFTBRACKET:
                        # Decrease darkness (more light)
                        lighting_system.adjust_darkness(-20)
                    elif event.key == K_RIGHTBRACKET:
                        # Increase darkness (less light)
                        lighting_system.adjust_darkness(20)
                    else:
                        # Handle game input
                        game.player.handle_keydown(event.key, game)

                elif game_state == "paused":
                    action = menu_system.handle_event(event)
                    if action == "resume":
                        game_state = "playing"
                    elif action == "save_and_exit":
                        # Save and return to main menu
                        if current_world_name:
                            world_manager.save_world(game, current_world_name)
                        game = None
                        current_world_name = None
                        game_state = "menu"
                        menu_system.reset_to_main_menu()
                    elif action == "exit_no_save":
                        # Return to main menu without saving
                        game = None
                        current_world_name = None
                        game_state = "menu"
                        menu_system.reset_to_main_menu()

            elif event.type == KEYUP and game_state == "playing" and game:
                game.player.handle_keyup(event.key, game)

        # Update and draw based on current state
        if game_state == "menu":
            menu_system.draw()

        elif game_state == "playing" and game:
            # Update game state
            game.player.update(dt, game)
            game.camera.update(game.player.world_x, game.player.world_y, dt)
            game._generate_chunks_around_player()

            # Update lighting system
            # lighting_system.update_player_light(game.player)  # Disabled - player no longer has light

            # Update day cycle if present
            if hasattr(game, "update_day_cycle"):
                game.update_day_cycle(dt)

            # Draw game
            draw_game(screen, game)

        elif game_state == "paused":
            # Draw game in background (frozen)
            if game:
                draw_game(screen, game)
            # Draw pause menu on top
            menu_system.draw()

        pygame.display.flip()


def draw_game(screen, game):
    """Draw the game world"""
    screen.fill(BLACK)

    # Draw world - only visible blocks
    left, right, top, bottom = game.camera.get_visible_bounds()

    for world_y in range(top, bottom + 1):
        for world_x in range(left, right + 1):
            screen_x, screen_y = game.camera.world_to_screen(world_x, world_y)
            # Only draw if on screen (within game area)
            if (
                -GRID_SIZE < screen_x < WINDOW_SIZE[0]
                and -GRID_SIZE < screen_y < GAME_HEIGHT
            ):
                block = game.get_block(world_x, world_y)
                if block:
                    # Check if this block is being mined
                    is_being_mined = (
                        game.player.is_mining
                        and game.player.mining_target == (world_x, world_y)
                    )
                    mining_progress = 0.0
                    if is_being_mined and block.minable:
                        mining_progress = 1.0 - (
                            block.current_health / block.max_health
                        )

                    draw_block(
                        screen_x, screen_y, block, is_being_mined, mining_progress
                    )

    # Draw targeting border around the block the player is facing
    target_x, target_y = game.player.get_target_position()
    target_screen_x, target_screen_y = game.camera.world_to_screen(target_x, target_y)

    # Only draw if target is on screen
    if (
        -GRID_SIZE < target_screen_x < WINDOW_SIZE[0]
        and -GRID_SIZE < target_screen_y < GAME_HEIGHT
    ):
        target_block = game.get_block(target_x, target_y)
        if target_block:  # Only show border if there's actually a block there
            # Draw a subtle border - light gray, thin line
            border_rect = pygame.Rect(
                target_screen_x, target_screen_y, GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(screen, (200, 200, 200), border_rect, 2)

    # Apply lighting effect
    lighting_system.apply_lighting(screen, game.camera)

    # Draw player (after lighting, so player is visible in darkness)
    player_screen_x, player_screen_y = game.camera.world_to_screen(
        game.player.world_x, game.player.world_y
    )

    # Try to use sprite first, fall back to colored rectangle
    player_sprite = game.player.get_current_sprite()
    if player_sprite:
        # Center the sprite in the grid cell
        sprite_rect = player_sprite.get_rect()
        sprite_rect.center = (
            player_screen_x + GRID_SIZE // 2,
            player_screen_y + GRID_SIZE // 2,
        )
        screen.blit(player_sprite, sprite_rect)
    else:
        # Fallback to colored rectangle with orientation arrow
        player_rect = pygame.Rect(
            player_screen_x + 2, player_screen_y + 2, GRID_SIZE - 4, GRID_SIZE - 4
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

    # Draw inventory (UI should be on top of lighting)
    draw_inventory(screen, game.player)


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
            block_rect = pygame.Rect(
                slot_x + 5, slot_y + 5, slot_size - 10, slot_size - 30
            )
            pygame.draw.rect(screen, temp_block.color, block_rect)

            # Draw count text
            font = pygame.font.Font(None, 24)
            count_text = font.render(str(count), True, WHITE)
            text_x = slot_x + slot_size // 2 - count_text.get_width() // 2
            text_y = slot_y + slot_size - 20
            screen.blit(count_text, (text_x, text_y))

    # Draw lighting level indicator
    font_small = pygame.font.Font(None, 24)
    darkness_pct = lighting_system.get_darkness_percentage()
    lighting_text = font_small.render(
        f"Lighting: {100-darkness_pct}% ([ ] to adjust)", True, WHITE
    )
    screen.blit(lighting_text, (10, GAME_HEIGHT + INVENTORY_HEIGHT - 30))


if __name__ == "__main__":
    main()
