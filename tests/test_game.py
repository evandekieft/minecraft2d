from game import Game
from player import Player
from camera import Camera
from block import Block


class TestGame:
    def test_game_initialization(self):
        game = Game()
        assert game.player is not None
        assert game.camera is not None
        assert game.chunk_size == 16
        assert isinstance(game.chunks, dict)
        assert len(game.chunks) == 25  # 5x5 initial chunks

    def test_chunk_generation_consistency(self):
        game = Game()

        # Get the same block multiple times
        block1 = game.get_block(0, 0)
        block2 = game.get_block(0, 0)
        block3 = game.get_block(0, 0)

        # Should be the same block type due to seeded generation
        assert block1.type == block2.type == block3.type

    def test_seeded_world_generation(self):
        # Create two separate games
        game1 = Game()
        game2 = Game()

        # Same coordinates should produce same block types
        for x in range(-5, 6):
            for y in range(-5, 6):
                block1 = game1.get_block(x, y)
                block2 = game2.get_block(x, y)
                assert block1.type == block2.type

    def test_chunk_boundaries(self):
        game = Game()

        # Test blocks at chunk boundaries
        block_0_0 = game.get_block(0, 0)
        block_15_15 = game.get_block(15, 15)
        block_16_16 = game.get_block(16, 16)

        # All should be valid blocks
        assert block_0_0 is not None
        assert block_15_15 is not None
        assert block_16_16 is not None

    def test_chunk_coordinate_calculation(self):
        game = Game()

        # Test chunk coordinate calculation
        assert game.get_block(0, 0) is not None  # Chunk (0, 0)
        assert game.get_block(15, 15) is not None  # Chunk (0, 0)
        assert game.get_block(16, 16) is not None  # Chunk (1, 1)
        assert game.get_block(-1, -1) is not None  # Chunk (-1, -1)

    def test_negative_coordinates(self):
        game = Game()

        # Test negative world coordinates
        block = game.get_block(-10, -10)
        assert block is not None
        # With noise generation, any valid block type is acceptable
        valid_types = {
            "water",
            "sand",
            "grass",
            "dirt",
            "wood",
            "stone",
            "coal",
            "lava",
            "diamond",
        }
        assert block.type in valid_types

    def test_block_type_distribution(self):
        game = Game()

        # Sample many blocks to verify realistic distribution with noise generation
        block_types = []
        for x in range(-50, 51):  # Wider range for noise-based generation
            for y in range(-50, 51):
                block = game.get_block(x, y)
                block_types.append(block.type)

        # Count all block types
        unique_types = set(block_types)
        total = len(block_types)

        # With noise generation, we should have multiple terrain types
        assert (
            len(unique_types) >= 3
        ), f"Expected at least 3 terrain types, got: {unique_types}"

        # Grass should still be the most common, but distribution will vary
        grass_count = block_types.count("grass")
        grass_ratio = grass_count / total
        assert grass_ratio > 0.3, f"Grass ratio too low: {grass_ratio}"

    def test_chunk_generation_on_demand(self):
        game = Game()
        initial_chunk_count = len(game.chunks)

        # Access a far-away block to trigger new chunk generation
        game.get_block(100, 100)

        # Should have generated a new chunk
        assert len(game.chunks) > initial_chunk_count

    def test_player_chunk_area_generation(self):
        game = Game()

        # Move player to a new area
        game.player.world_x = 50
        game.player.world_y = 50

        initial_chunk_count = len(game.chunks)
        game._generate_chunks_around_player()

        # Should generate new chunks around the player
        assert len(game.chunks) > initial_chunk_count

    def test_chunk_storage_format(self):
        game = Game()

        # Access a block to ensure chunk is generated
        game.get_block(0, 0)

        # Check chunk storage format
        chunk = game.chunks[(0, 0)]
        assert isinstance(chunk, dict)
        assert (0, 0) in chunk  # Local coordinates
        assert isinstance(chunk[(0, 0)], Block)


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



class TestBlockReplacement:
    def test_replace_block_success(self):
        game = Game()

        # Ensure there's a block at (0, 0)
        original_block = game.get_block(0, 0)
        assert original_block is not None
        original_type = original_block.type

        # Replace it with a different type
        new_type = "dirt" if original_type != "dirt" else "grass"
        result = game.replace_block(0, 0, new_type)

        assert result is True
        new_block = game.get_block(0, 0)
        assert new_block.type == new_type

    def test_replace_block_nonexistent_chunk(self):
        game = Game()

        # Try to replace a block in a chunk that doesn't exist
        result = game.replace_block(1000, 1000, "dirt")

        assert result is False

    def test_replace_block_maintains_chunk_structure(self):
        game = Game()

        # Replace a block and ensure chunk structure is maintained
        game.replace_block(0, 0, "wood")

        # Should still be able to access the block
        block = game.get_block(0, 0)
        assert block is not None
        assert block.type == "wood"

        # Should still be able to access neighboring blocks
        neighbor = game.get_block(1, 0)
        assert neighbor is not None

    def test_replace_block_with_all_new_types(self):
        game = Game()

        # Test replacing with all new block types
        new_block_types = ["sand", "wood", "stone", "coal", "lava", "diamond", "water"]

        for i, block_type in enumerate(new_block_types):
            x, y = i, 0
            result = game.replace_block(x, y, block_type)

            assert result is True
            block = game.get_block(x, y)
            assert block is not None
            assert block.type == block_type

    def test_new_block_types_properties(self):
        game = Game()

        # Test that new block types have correct properties
        test_cases = [
            ("sand", True, False),  # walkable, not minable
            ("wood", False, True),  # not walkable, minable
            ("stone", False, True),  # not walkable, minable
            ("coal", False, True),  # not walkable, minable
            ("lava", False, False),  # not walkable, not minable
            ("diamond", False, True),  # not walkable, minable
            ("water", False, False),  # not walkable, not minable
        ]

        for block_type, expected_walkable, expected_minable in test_cases:
            game.replace_block(0, 0, block_type)
            block = game.get_block(0, 0)

            assert (
                block.walkable == expected_walkable
            ), f"{block_type} walkable mismatch"
            assert block.minable == expected_minable, f"{block_type} minable mismatch"
