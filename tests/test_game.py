import pygame
from unittest.mock import Mock, patch
from game import Game


class TestGameLoop:
    """Test the main game loop functionality"""
    
    def test_game_initialization_with_screen(self, pygame_setup):
        """Test game initialization with a provided screen"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        
        assert game.screen == screen
        assert game.running == True
        assert game.game_state == "menu"
        assert game.current_world_name is None
        assert game.current_game_world is None
    
    def test_game_initialization_without_screen(self, pygame_setup):
        """Test game initialization without provided screen"""
        with patch('pygame.display.set_mode') as mock_set_mode:
            mock_screen = Mock()
            mock_set_mode.return_value = mock_screen
            
            game = Game()
            
            assert game.screen == mock_screen
            assert game.running == True
            assert game.game_state == "menu"
    
    def test_quit_method(self, pygame_setup):
        """Test the quit method"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        
        with patch('pygame.quit') as mock_quit, \
             patch('sys.exit') as mock_exit:
            
            game.quit()
            
            assert game.running == False
            mock_quit.assert_called_once()
            mock_exit.assert_called_once()
    
    def test_quit_with_world_save(self, pygame_setup):
        """Test quit method saves world when in playing state"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        
        # Set up a game world and mock the world manager
        game.current_game_world = Mock()
        game.current_world_name = "test_world"
        game.game_state = "playing"
        game.world_manager.save_world = Mock()
        
        with patch('pygame.quit') as mock_quit, \
             patch('sys.exit') as mock_exit:
            
            game.quit()
            
            # Should save the world
            game.world_manager.save_world.assert_called_once_with(
                game.current_game_world, "test_world"
            )
            mock_quit.assert_called_once()
            mock_exit.assert_called_once()


class TestEventHandling:
    """Test event handling in the game loop"""
    
    def test_handle_keydown_menu_quit(self, pygame_setup):
        """Test handling keydown quit action in menu"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        
        # Mock menu system returning quit action
        game.menu_system.handle_event = Mock(return_value="quit")
        
        keydown_event = Mock()
        keydown_event.key = pygame.K_ESCAPE
        
        with patch('pygame.quit') as mock_quit, \
             patch('sys.exit') as mock_exit:
            
            game._handle_keydown(keydown_event)
            
            mock_quit.assert_called_once()
            mock_exit.assert_called_once()
    
    def test_handle_keydown_create_world(self, pygame_setup):
        """Test handling create world action"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        
        # Mock menu system returning create world action with no name
        game.menu_system.handle_event = Mock(return_value=("create_world", None))
        game.world_manager.create_new_world_unsaved = Mock(return_value=Mock())
        
        keydown_event = Mock()
        keydown_event.key = pygame.K_RETURN
        
        game._handle_keydown(keydown_event)
        
        assert game.game_state == "playing"
        assert game.current_world_name is None  # No name until saved
        assert game.current_game_world is not None
    
    def test_handle_keydown_load_world(self, pygame_setup):
        """Test handling load world action"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        
        # Mock menu system returning load world action
        game.menu_system.handle_event = Mock(return_value=("load_world", "existing_world"))
        game.world_manager.load_world = Mock(return_value=Mock())
        
        keydown_event = Mock()
        keydown_event.key = pygame.K_RETURN
        
        game._handle_keydown(keydown_event)
        
        assert game.game_state == "playing"
        assert game.current_world_name == "existing_world"
        assert game.current_game_world is not None
    
    def test_handle_keydown_playing_escape(self, pygame_setup):
        """Test handling escape key in playing state"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        game.game_state = "playing"
        game.current_game_world = Mock()
        
        keydown_event = Mock()
        keydown_event.key = pygame.K_ESCAPE
        
        game._handle_keydown(keydown_event)
        
        assert game.game_state == "paused"
    
    def test_handle_keydown_playing_game_input(self, pygame_setup):
        """Test handling game input in playing state"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        game.game_state = "playing"
        game.current_game_world = Mock()
        
        keydown_event = Mock()
        keydown_event.key = pygame.K_w
        
        game._handle_keydown(keydown_event)
        
        # Should pass event to game world player
        game.current_game_world.player.handle_keydown.assert_called_once_with(
            pygame.K_w, game.current_game_world
        )
    
    def test_handle_keydown_paused_resume(self, pygame_setup):
        """Test handling resume action in paused state"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        game.game_state = "paused"
        
        # Mock menu system returning resume action
        game.menu_system.handle_event = Mock(return_value="resume")
        
        keydown_event = Mock()
        keydown_event.key = pygame.K_RETURN
        
        game._handle_keydown(keydown_event)
        
        assert game.game_state == "playing"
    
    def test_handle_keydown_paused_save_and_exit(self, pygame_setup):
        """Test handling save and exit action in paused state"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        game.game_state = "paused"
        game.current_game_world = Mock()
        game.current_world_name = None  # No name yet for new worlds
        
        # Mock menu system returning save and exit action with world name
        game.menu_system.handle_event = Mock(return_value=("save_and_exit", "test_world"))
        game.world_manager.save_world = Mock()
        
        keydown_event = Mock()
        keydown_event.key = pygame.K_RETURN
        
        game._handle_keydown(keydown_event)
        
        assert game.game_state == "menu"
        assert game.current_game_world is None
        assert game.current_world_name is None
        game.world_manager.save_world.assert_called_once()
    
    def test_handle_keyup_playing(self, pygame_setup):
        """Test handling keyup events in playing state"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        game.game_state = "playing"
        game.current_game_world = Mock()
        
        keyup_event = Mock()
        keyup_event.key = pygame.K_w
        
        game._handle_keyup(keyup_event)
        
        # Should pass event to game world player
        game.current_game_world.player.handle_keyup.assert_called_once_with(
            pygame.K_w, game.current_game_world
        )
    
    def test_handle_resize_event(self, pygame_setup):
        """Test handling window resize events"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        game.game_state = "playing"
        game.current_game_world = Mock()
        
        resize_event = Mock()
        resize_event.w = 1200
        resize_event.h = 800
        
        with patch('pygame.display.set_mode') as mock_set_mode:
            mock_new_screen = Mock()
            mock_set_mode.return_value = mock_new_screen
            
            game._handle_resize(resize_event)
            
            assert game.screen == mock_new_screen
            game.current_game_world.handle_window_resize.assert_called_once_with(1200, 800)
    
    def test_handle_resize_minimum_size(self, pygame_setup):
        """Test resize event respects minimum window size"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        
        resize_event = Mock()
        resize_event.w = 500  # Below minimum
        resize_event.h = 400  # Below minimum
        
        with patch('pygame.display.set_mode') as mock_set_mode:
            game._handle_resize(resize_event)
            
            # Should enforce minimum size
            mock_set_mode.assert_called_once_with((800, 600), pygame.RESIZABLE)


class TestGameUpdates:
    """Test game update and render functionality"""
    
    def test_update_playing_state(self, pygame_setup):
        """Test update method in playing state"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        game.game_state = "playing"
        game.current_game_world = Mock()
        
        dt = 0.016
        game._update(dt)
        
        game.current_game_world.update_state.assert_called_once_with(dt)
    
    def test_update_menu_state(self, pygame_setup):
        """Test update method in menu state"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        game.game_state = "menu"
        
        dt = 0.016
        game._update(dt)
        
        # Should not crash when no game world exists
        assert True  # Just checking no exception is thrown
    
    def test_render_menu_state(self, pygame_setup):
        """Test render method in menu state"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        game.game_state = "menu"
        game.menu_system.draw = Mock()
        
        game._render()
        
        game.menu_system.draw.assert_called_once()
    
    def test_render_playing_state(self, pygame_setup):
        """Test render method in playing state"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        game.game_state = "playing"
        game.current_game_world = Mock()
        
        game._render()
        
        game.current_game_world.draw.assert_called_once_with(screen)
    
    def test_render_paused_state(self, pygame_setup):
        """Test render method in paused state"""
        screen = pygame.Surface((800, 600))
        game = Game(screen=screen)
        game.game_state = "paused"
        game.current_game_world = Mock()
        game.menu_system.draw = Mock()
        
        game._render()
        
        game.current_game_world.draw.assert_called_once_with(screen)
        game.menu_system.draw.assert_called_once()