import pygame
import sys
from pygame.locals import (
    QUIT,
    KEYDOWN,
    KEYUP,
    K_ESCAPE,
    K_c,
    VIDEORESIZE,
    MOUSEBUTTONDOWN,
    MOUSEMOTION,
)
from menu import MenuSystem
from world_storage import WorldStorage
from crafting_ui import CraftingUI
from constants import WINDOW_SIZE
from enum import Enum


class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    CRAFTING = "crafting"


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
        self.world_manager: WorldStorage = WorldStorage()
        self.menu_system: MenuSystem = MenuSystem(self.world_manager)
        self.crafting_ui: CraftingUI = CraftingUI(WINDOW_SIZE[0], WINDOW_SIZE[1])

        self.clock = pygame.time.Clock()

        # Game state management
        self.running = True
        self.game_state: GameState = GameState.MENU
        self.current_game_world = None  # The actual GameWorld instance for the world

        # Do an initial render to populate menu clickable areas (only if we have a real screen)
        if hasattr(self.screen, "get_size"):
            self._render()
            pygame.display.flip()

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

            elif event.type in (MOUSEBUTTONDOWN, MOUSEMOTION):
                self._handle_mouse(event)

    def _handle_mouse(self, event):
        """Handle mouse events"""
        if self.game_state == GameState.CRAFTING and self.current_game_world:
            # Handle crafting UI mouse events
            self.crafting_ui.handle_event(
                event, self.current_game_world.player.inventory
            )
        else:
            # Handle menu mouse events
            action = self.menu_system.handle_event(event)
            if action:
                # Reuse the same action handling as keyboard events
                self._handle_menu_action(action)

    def _handle_menu_action(self, action):
        """Handle menu actions (from both keyboard and mouse)"""
        if action == "quit":
            self.quit()
        elif action == "resume":
            self.game_state = GameState.PLAYING
        elif action == "exit_no_save":
            self.current_game_world = None
            self.current_world_name = None
            self.game_state = GameState.MENU
            self.menu_system.reset_to_main_menu()
        elif isinstance(action, tuple):
            action_type, data = action
            if action_type == "load_world":
                if data:
                    self.current_game_world = self.world_manager.load_world(data)
                    if self.current_game_world:
                        self.game_state = GameState.PLAYING
                        self.menu_system.reset_to_main_menu()
            elif action_type == "create_world":
                # Create world without saving it yet (no name)
                self.current_game_world = self.world_manager.create_new_world_unsaved()
                if self.current_game_world:
                    self.current_world_name = None  # No name yet
                    self.game_state = GameState.PLAYING
                    self.menu_system.reset_to_main_menu()
            elif action_type == "save_and_exit":
                # Save with the provided world name
                world_name = data
                if self.current_game_world:
                    self.world_manager.save_world(self.current_game_world, world_name)
                self.current_game_world = None
                self.current_world_name = None
                self.game_state = GameState.MENU
                self.menu_system.reset_to_main_menu()

    def _handle_keydown(self, event):
        """Handle keydown events"""
        if self.game_state == GameState.MENU:
            action = self.menu_system.handle_event(event)
            if action:
                self._handle_menu_action(action)

        elif self.game_state == GameState.PLAYING:
            if event.key == K_ESCAPE:
                self.menu_system.show_pause_menu()
                self.game_state = GameState.PAUSED
            elif event.key == K_c:
                self.game_state = GameState.CRAFTING
            elif self.current_game_world:
                self.current_game_world.player.handle_keydown(
                    event.key, self.current_game_world
                )

        elif self.game_state == GameState.PAUSED:
            action = self.menu_system.handle_event(event)
            if action:
                self._handle_menu_action(action)

        elif self.game_state == GameState.CRAFTING:
            if event.key == K_ESCAPE or event.key == K_c:
                self.game_state = GameState.PLAYING
            elif self.current_game_world:
                # Handle crafting UI events
                self.crafting_ui.handle_event(
                    event, self.current_game_world.player.inventory
                )

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
            GameState.CRAFTING,
        ]:
            self.current_game_world.handle_window_resize(new_width, new_height)

        # Update menu system
        self.menu_system.handle_window_resize(new_width, new_height)

        # Update crafting UI
        self.crafting_ui.handle_window_resize(new_width, new_height)

    def _update(self, dt):
        """Update game state"""
        if self.game_state == GameState.PLAYING and self.current_game_world:
            self.current_game_world.update_state(dt)

    def _render(self):
        """Render the game"""
        if self.game_state == GameState.MENU:
            self.menu_system.draw(self.screen)
        elif self.game_state == GameState.PLAYING and self.current_game_world:
            self.current_game_world.draw(self.screen)
        elif self.game_state == GameState.PAUSED:
            # Draw game in background (frozen)
            if self.current_game_world:
                self.current_game_world.draw(self.screen)
            # Draw pause menu on top
            self.menu_system.draw(self.screen)
        elif self.game_state == GameState.CRAFTING:
            # Draw game in background (frozen)
            if self.current_game_world:
                self.current_game_world.draw(self.screen)
                # Draw crafting modal on top
                self.crafting_ui.draw(
                    self.screen, self.current_game_world.player.inventory
                )
