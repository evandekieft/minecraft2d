import pytest
from world import Game
from player import Player
from camera import Camera


class TestGameIntegration:
    def test_game_components_initialization(self):
        game = Game()

        # Test that all components are properly initialized
        assert isinstance(game.player, Player)
        assert isinstance(game.camera, Camera)
        assert game.player.world_x == 0
        assert game.player.world_y == 0
        assert game.camera.x == 0.0
        assert game.camera.y == 0.0

    def test_player_game_interaction(self):
        game = Game()
        initial_x = game.player.world_x
        initial_y = game.player.world_y

        # Ensure player is on walkable ground
        current_block = game.get_block(initial_x, initial_y)
        if current_block and not current_block.walkable:
            # If starting on unwalkable block, move to walkable one
            game.player.world_x = 0
            game.player.world_y = 0

        # Find a walkable block to move to
        walkable_found = False
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                test_x = game.player.world_x + dx
                test_y = game.player.world_y + dy
                test_block = game.get_block(test_x, test_y)
                if test_block and test_block.walkable:
                    # Test movement to walkable block
                    game.player.move(dx, dy, game)
                    assert game.player.world_x == test_x
                    assert game.player.world_y == test_y
                    walkable_found = True
                    break
            if walkable_found:
                break

        # Should have found at least one walkable block nearby
        assert walkable_found

    def test_camera_follows_player(self):
        game = Game()

        # Move player
        game.player.world_x = 10
        game.player.world_y = 20

        # Update camera
        game.camera.update(game.player.world_x, game.player.world_y, 0.016)

        # Camera should move toward player
        assert game.camera.x != 0.0 or game.camera.y != 0.0

    def test_world_generation_around_player(self):
        game = Game()
        initial_chunks = len(game.chunks)

        # Move player far away
        game.player.world_x = 100
        game.player.world_y = 100

        # Generate chunks around new player position
        game._generate_chunks_around_player()

        # Should have generated new chunks
        assert len(game.chunks) > initial_chunks

    def test_player_collision_system(self):
        game = Game()

        # Test collision with different block types
        # This tests the integration between player movement and world state
        start_x = game.player.world_x
        start_y = game.player.world_y

        # Try to move in each direction
        moves_tested = 0
        successful_moves = 0

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            target_x = start_x + dx
            target_y = start_y + dy
            block = game.get_block(target_x, target_y)

            if block:
                moves_tested += 1
                game.player.move(dx, dy, game)

                if block.walkable:
                    # Should have moved
                    assert game.player.world_x == target_x
                    assert game.player.world_y == target_y
                    successful_moves += 1
                    # Move back for next test
                    game.player.world_x = start_x
                    game.player.world_y = start_y
                else:
                    # Should not have moved
                    assert game.player.world_x == start_x
                    assert game.player.world_y == start_y

        # Should have tested at least one move
        assert moves_tested > 0

    def test_chunk_generation_consistency_with_player(self):
        game = Game()

        # Get initial chunk count
        initial_chunks = len(game.chunks)

        # Move player to edge of generated area
        game.player.world_x = 32  # Two chunks away
        game.player.world_y = 32

        # Generate chunks around player
        game._generate_chunks_around_player()

        # Should have generated new chunks
        final_chunks = len(game.chunks)
        assert final_chunks > initial_chunks

        # Player should be able to access blocks in new area
        block = game.get_block(game.player.world_x, game.player.world_y)
        assert block is not None
        assert block.type in ["grass", "tree"]

    def test_game_state_persistence(self):
        game = Game()

        # Make changes to game state
        original_x = game.player.world_x
        original_y = game.player.world_y

        # Move player
        game.player.world_x = 5
        game.player.world_y = 10

        # Update camera
        game.camera.update(game.player.world_x, game.player.world_y, 0.016)

        # State should be maintained
        assert game.player.world_x == 5
        assert game.player.world_y == 10
        assert game.camera.x != 0.0 or game.camera.y != 0.0

        # World should still be accessible
        block = game.get_block(5, 10)
        assert block is not None

    def test_boundary_conditions(self):
        game = Game()

        # Test extreme coordinates
        extreme_coords = [
            (0, 0),
            (1000, 1000),
            (-1000, -1000),
            (500, -500),
            (-500, 500),
        ]

        for x, y in extreme_coords:
            block = game.get_block(x, y)
            assert block is not None
            assert block.type in ["grass", "tree"]

    def test_multiple_chunk_generation_cycles(self):
        game = Game()

        # Simulate player moving around, triggering multiple chunk generations
        positions = [(0, 0), (50, 0), (50, 50), (0, 50), (-50, 0), (-50, -50)]

        for x, y in positions:
            game.player.world_x = x
            game.player.world_y = y
            game._generate_chunks_around_player()

            # Should always be able to access player position
            block = game.get_block(x, y)
            assert block is not None
            assert block.type in ["grass", "tree"]

        # Should have generated many chunks
        assert len(game.chunks) > 9  # More than initial 3x3
