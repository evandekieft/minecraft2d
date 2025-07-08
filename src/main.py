import pygame
import sys
from pygame.locals import QUIT, KEYDOWN, KEYUP, K_ESCAPE
from constants import WINDOW_SIZE
from menu import MenuSystem
from world_manager import WorldManager

# Initialize PyGame
pygame.init()

# Set up the display
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Minecraft2D")



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

            # Update day cycle
            game.update_day_cycle(dt)

            # Draw game
            game.draw(screen)

        elif game_state == "paused":
            # Draw game in background (frozen)
            if game:
                game.draw(screen)
            # Draw pause menu on top
            menu_system.draw()

        pygame.display.flip()



if __name__ == "__main__":
    main()
