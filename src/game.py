import pygame
import sys
from pygame.locals import QUIT, KEYDOWN, KEYUP, K_ESCAPE, VIDEORESIZE
from menu import MenuSystem
from world_manager import WorldManager
from constants import WINDOW_SIZE
from enum import Enum


class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"


class Game:
    """Main game application that manages the game loop and UI"""

    def __init__(self, screen=None):
        # Initialize screen (for testing, can be provided)
        if screen is None:
            self.screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
            pygame.display.set_caption("Minecraft2D")
        else:
            self.screen = screen

        # Initialize game systems
        self.menu_system: MenuSystem = MenuSystem(self.screen)
        self.world_manager: WorldManager = WorldManager()
        self.clock = pygame.time.Clock()

        # Game state management
        self.running = True
        self.game_state: GameState = GameState.MENU
        self.current_world_name = None
        self.current_game_world = None  # The actual GameWorld instance for the world

    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self._handle_events()
            self._update(dt)
            self._render()
            pygame.display.flip()

    def quit(self):
        """Quit the game"""
        # Save before quitting only if world has a name
        if (
            self.current_game_world
            and self.current_world_name  # Only save if world has been named
            and self.game_state == "playing"
        ):
            self.world_manager.save_world(
                self.current_game_world, self.current_world_name
            )
        self.running = False
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit()

            elif event.type == KEYDOWN:
                self._handle_keydown(event)

            elif event.type == KEYUP:
                self._handle_keyup(event)

            elif event.type == VIDEORESIZE:
                self._handle_resize(event)

    def _handle_keydown(self, event):
        """Handle keydown events"""
        if self.game_state == GameState.MENU:
            action = self.menu_system.handle_event(event)
            if action == "quit":
                self.quit()
            elif isinstance(action, tuple):
                action_type, data = action
                if action_type == "load_world":
                    self.current_game_world = self.world_manager.load_world(data)
                    if self.current_game_world:
                        self.current_world_name = data
                        self.game_state = GameState.PLAYING
                        self.menu_system.reset_to_main_menu()
                elif action_type == "create_world":
                    # Create world without saving it yet (no name)
                    self.current_game_world = (
                        self.world_manager.create_new_world_unsaved()
                    )
                    if self.current_game_world:
                        self.current_world_name = None  # No name yet
                        self.game_state = GameState.PLAYING
                        self.menu_system.reset_to_main_menu()

        elif self.game_state == GameState.PLAYING:
            if event.key == K_ESCAPE:
                self.menu_system.show_pause_menu()
                self.game_state = GameState.PAUSED
            elif self.current_game_world:
                self.current_game_world.player.handle_keydown(
                    event.key, self.current_game_world
                )

        elif self.game_state == GameState.PAUSED:
            action = self.menu_system.handle_event(event)
            if action == "resume":
                self.game_state = GameState.PLAYING
            elif isinstance(action, tuple) and action[0] == "save_and_exit":
                # Save with the provided world name
                world_name = action[1]
                self.world_manager.save_world(self.current_game_world, world_name)
                self.current_game_world = None
                self.current_world_name = None
                self.game_state = GameState.MENU
                self.menu_system.reset_to_main_menu()
            elif action == "exit_no_save":
                self.current_game_world = None
                self.current_world_name = None
                self.game_state = GameState.MENU
                self.menu_system.reset_to_main_menu()

    def _handle_keyup(self, event):
        """Handle keyup events"""
        if self.game_state == GameState.PLAYING and self.current_game_world:
            self.current_game_world.player.handle_keyup(
                event.key, self.current_game_world
            )

    def _handle_resize(self, event):
        """Handle window resize events"""
        new_width, new_height = event.w, event.h

        # Enforce minimum window size
        min_width, min_height = 800, 600
        new_width = max(new_width, min_width)
        new_height = max(new_height, min_height)

        # Update screen
        self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)

        # Update game components if game is active
        if self.current_game_world and self.game_state in [
            GameState.PLAYING,
            GameState.PAUSED,
        ]:
            self.current_game_world.handle_window_resize(new_width, new_height)

        # Update menu system
        self.menu_system.handle_window_resize(self.screen, new_width, new_height)

    def _update(self, dt):
        """Update game state"""
        if self.game_state == GameState.PLAYING and self.current_game_world:
            self.current_game_world.update_state(dt)

    def _render(self):
        """Render the game"""
        if self.game_state == GameState.MENU:
            self.menu_system.draw()
        elif self.game_state == GameState.PLAYING and self.current_game_world:
            self.current_game_world.draw(self.screen)
        elif self.game_state == GameState.PAUSED:
            # Draw game in background (frozen)
            if self.current_game_world:
                self.current_game_world.draw(self.screen)
            # Draw pause menu on top
            self.menu_system.draw()
