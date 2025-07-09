import pygame
from game_world import GameWorld
from player import Player
from camera import Camera
from block import Block
from block_type import BlockType


class TestGameWorld:
    def test_game_world_initialization(self):
        game_world = GameWorld()
        assert game_world.player is not None
        assert game_world.camera is not None
        assert game_world.chunk_size == 16
        assert isinstance(game_world.chunks, dict)
        assert len(game_world.chunks) == 25  # 5x5 initial chunks

    def test_chunk_generation_consistency(self):
        game_world = GameWorld()

        # Get the same block multiple times
        block1 = game_world.get_block(0, 0)
        block2 = game_world.get_block(0, 0)
        block3 = game_world.get_block(0, 0)

        # Should be the same block type due to seeded generation
        assert block1.type == block2.type == block3.type

    def test_seeded_world_generation(self):
        # Create two separate game worlds
        game_world1 = GameWorld()
        game_world2 = GameWorld()

        # Same coordinates should produce same block types
        for x in range(-5, 6):
            for y in range(-5, 6):
                block1 = game_world1.get_block(x, y)
                block2 = game_world2.get_block(x, y)
                assert block1.type == block2.type

    def test_chunk_boundaries(self):
        game_world = GameWorld()

        # Test blocks at chunk boundaries
        block_0_0 = game_world.get_block(0, 0)
        block_15_15 = game_world.get_block(15, 15)
        block_16_16 = game_world.get_block(16, 16)

        # All should be valid blocks
        assert block_0_0 is not None
        assert block_15_15 is not None
        assert block_16_16 is not None

    def test_chunk_coordinate_calculation(self):
        game_world = GameWorld()

        # Test chunk coordinate calculation
        assert game_world.get_block(0, 0) is not None  # Chunk (0, 0)
        assert game_world.get_block(15, 15) is not None  # Chunk (0, 0)
        assert game_world.get_block(16, 16) is not None  # Chunk (1, 1)
        assert game_world.get_block(-1, -1) is not None  # Chunk (-1, -1)

    def test_negative_coordinates(self):
        game_world = GameWorld()

        # Test negative world coordinates
        block = game_world.get_block(-10, -10)
        assert block is not None
        # With noise generation, any valid block type is acceptable
        valid_types = {
            BlockType.WATER,
            BlockType.SAND,
            BlockType.GRASS,
            BlockType.DIRT,
            BlockType.WOOD,
            BlockType.STONE,
            BlockType.COAL,
            BlockType.LAVA,
            BlockType.DIAMOND,
        }
        assert block.type in valid_types

    def test_block_type_distribution(self):
        game_world = GameWorld()

        # Sample many blocks to verify realistic distribution with noise generation
        block_types = []
        for x in range(-50, 51):  # Wider range for noise-based generation
            for y in range(-50, 51):
                block = game_world.get_block(x, y)
                block_types.append(block.type)

        # Count all block types
        unique_types = set(block_types)
        total = len(block_types)

        # With noise generation, we should have multiple terrain types
        assert (
            len(unique_types) >= 3
        ), f"Expected at least 3 terrain types, got: {unique_types}"

        # Grass should still be the most common, but distribution will vary
        grass_count = block_types.count(BlockType.GRASS)
        grass_ratio = grass_count / total
        assert grass_ratio > 0.3, f"Grass ratio too low: {grass_ratio}"

    def test_chunk_generation_on_demand(self):
        game_world = GameWorld()
        initial_chunk_count = len(game_world.chunks)

        # Access a far-away block to trigger new chunk generation
        game_world.get_block(100, 100)

        # Should have generated a new chunk
        assert len(game_world.chunks) > initial_chunk_count

    def test_player_chunk_area_generation(self):
        game_world = GameWorld()

        # Move player to a new area
        game_world.player.world_x = 50
        game_world.player.world_y = 50

        initial_chunk_count = len(game_world.chunks)
        game_world._generate_chunks_around_player()

        # Should generate new chunks around the player
        assert len(game_world.chunks) > initial_chunk_count

    def test_chunk_storage_format(self):
        game_world = GameWorld()

        # Access a block to ensure chunk is generated
        game_world.get_block(0, 0)

        # Check chunk storage format
        chunk = game_world.chunks[(0, 0)]
        assert isinstance(chunk, dict)
        assert (0, 0) in chunk  # Local coordinates
        assert isinstance(chunk[(0, 0)], Block)


class TestGameWorldIntegration:
    def test_game_world_components_initialization(self):
        game_world = GameWorld()

        # Test that all components are properly initialized
        assert isinstance(game_world.player, Player)
        assert isinstance(game_world.camera, Camera)
        assert game_world.player.world_x == 0
        assert game_world.player.world_y == 0
        assert game_world.camera.x == 0.0
        assert game_world.camera.y == 0.0

    def test_player_game_world_interaction(self):
        game_world = GameWorld()
        initial_x = game_world.player.world_x
        initial_y = game_world.player.world_y

        # Ensure player is on walkable ground
        current_block = game_world.get_block(initial_x, initial_y)
        if current_block and not current_block.type.walkable:
            # If starting on unwalkable block, move to walkable one
            game_world.player.world_x = 0
            game_world.player.world_y = 0

        # Find a walkable block to move to
        walkable_found = False
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                test_x = game_world.player.world_x + dx
                test_y = game_world.player.world_y + dy
                test_block = game_world.get_block(test_x, test_y)
                if test_block and test_block.type.walkable:
                    # Test movement to walkable block
                    game_world.player.move(dx, dy, game_world)
                    assert game_world.player.world_x == test_x
                    assert game_world.player.world_y == test_y
                    walkable_found = True
                    break
            if walkable_found:
                break

        # Should have found at least one walkable block nearby
        assert walkable_found

    def test_camera_follows_player(self):
        game_world = GameWorld()

        # Move player
        game_world.player.world_x = 10
        game_world.player.world_y = 20

        # Update camera
        game_world.camera.update(game_world.player.world_x, game_world.player.world_y, 0.016)

        # Camera should move toward player
        assert game_world.camera.x != 0.0 or game_world.camera.y != 0.0

    def test_world_generation_around_player(self):
        game_world = GameWorld()
        initial_chunks = len(game_world.chunks)

        # Move player far away
        game_world.player.world_x = 100
        game_world.player.world_y = 100

        # Generate chunks around new player position
        game_world._generate_chunks_around_player()

        # Should have generated new chunks
        assert len(game_world.chunks) > initial_chunks

    def test_player_collision_system(self):
        game_world = GameWorld()

        # Test collision with different block types
        # This tests the integration between player movement and world state
        start_x = game_world.player.world_x
        start_y = game_world.player.world_y

        # Try to move in each direction
        moves_tested = 0
        successful_moves = 0

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            target_x = start_x + dx
            target_y = start_y + dy
            block = game_world.get_block(target_x, target_y)

            if block:
                moves_tested += 1
                game_world.player.move(dx, dy, game_world)

                if block.type.walkable:
                    # Should have moved
                    assert game_world.player.world_x == target_x
                    assert game_world.player.world_y == target_y
                    successful_moves += 1
                    # Move back for next test
                    game_world.player.world_x = start_x
                    game_world.player.world_y = start_y
                else:
                    # Should not have moved
                    assert game_world.player.world_x == start_x
                    assert game_world.player.world_y == start_y

        # Should have tested at least one move
        assert moves_tested > 0

    def test_chunk_generation_consistency_with_player(self):
        game_world = GameWorld()

        # Get initial chunk count
        initial_chunks = len(game_world.chunks)

        # Move player to edge of generated area
        game_world.player.world_x = 32  # Two chunks away
        game_world.player.world_y = 32

        # Generate chunks around player
        game_world._generate_chunks_around_player()

        # Should have generated new chunks
        final_chunks = len(game_world.chunks)
        assert final_chunks > initial_chunks

        # Player should be able to access blocks in new area
        block = game_world.get_block(game_world.player.world_x, game_world.player.world_y)
        assert block is not None
        assert block.type in [BlockType.GRASS, BlockType.WOOD]

    def test_game_world_state_persistence(self):
        game_world = GameWorld()

        # Make changes to game world state
        original_x = game_world.player.world_x
        original_y = game_world.player.world_y

        # Move player
        game_world.player.world_x = 5
        game_world.player.world_y = 10

        # Update camera
        game_world.camera.update(game_world.player.world_x, game_world.player.world_y, 0.016)

        # State should be maintained
        assert game_world.player.world_x == 5
        assert game_world.player.world_y == 10
        assert game_world.camera.x != 0.0 or game_world.camera.y != 0.0

        # World should still be accessible
        block = game_world.get_block(5, 10)
        assert block is not None

    def test_boundary_conditions(self):
        game_world = GameWorld()

        # Test extreme coordinates
        extreme_coords = [
            (0, 0),
            (1000, 1000),
            (-1000, -1000),
            (500, -500),
            (-500, 500),
        ]

        for x, y in extreme_coords:
            block = game_world.get_block(x, y)
            assert block is not None
            # Block should be a valid terrain type
            valid_types = [BlockType.GRASS, BlockType.WOOD, BlockType.SAND, BlockType.STONE, BlockType.WATER, BlockType.COAL, BlockType.DIAMOND, BlockType.LAVA]
            assert block.type in valid_types

    def test_multiple_chunk_generation_cycles(self):
        game_world = GameWorld()

        # Simulate player moving around, triggering multiple chunk generations
        positions = [(0, 0), (50, 0), (50, 50), (0, 50), (-50, 0), (-50, -50)]

        for x, y in positions:
            game_world.player.world_x = x
            game_world.player.world_y = y
            game_world._generate_chunks_around_player()

            # Should always be able to access player position
            block = game_world.get_block(x, y)
            assert block is not None
            assert block.type in [BlockType.GRASS, BlockType.WOOD, BlockType.SAND, BlockType.WATER, BlockType.STONE]

        # Should have generated many chunks
        assert len(game_world.chunks) > 9  # More than initial 3x3


class TestBlockReplacement:
    def test_replace_block_success(self):
        game_world = GameWorld()

        # Ensure there's a block at (0, 0)
        original_block = game_world.get_block(0, 0)
        assert original_block is not None
        original_type = original_block.type

        # Replace it with a different type
        new_type = BlockType.DIRT if original_type != BlockType.DIRT else BlockType.GRASS
        result = game_world.replace_block(0, 0, new_type)

        assert result is True
        new_block = game_world.get_block(0, 0)
        assert new_block.type == new_type

    def test_replace_block_nonexistent_chunk(self):
        game_world = GameWorld()

        # Try to replace a block in a chunk that doesn't exist
        result = game_world.replace_block(1000, 1000, BlockType.DIRT)

        assert result is False

    def test_replace_block_maintains_chunk_structure(self):
        game_world = GameWorld()

        # Replace a block and ensure chunk structure is maintained
        game_world.replace_block(0, 0, BlockType.WOOD)

        # Should still be able to access the block
        block = game_world.get_block(0, 0)
        assert block is not None
        assert block.type == BlockType.WOOD

        # Should still be able to access neighboring blocks
        neighbor = game_world.get_block(1, 0)
        assert neighbor is not None

    def test_replace_block_with_all_new_types(self):
        game_world = GameWorld()

        # Test replacing with all new block types
        new_block_types = [BlockType.SAND, BlockType.WOOD, BlockType.STONE, BlockType.COAL, BlockType.LAVA, BlockType.DIAMOND, BlockType.WATER]

        for i, block_type in enumerate(new_block_types):
            x, y = i, 0
            result = game_world.replace_block(x, y, block_type)

            assert result is True
            block = game_world.get_block(x, y)
            assert block is not None
            assert block.type == block_type

    def test_new_block_types_properties(self):
        game_world = GameWorld()

        # Test that new block types have correct properties
        test_cases = [
            (BlockType.SAND, True, False),  # walkable, not minable
            (BlockType.WOOD, False, True),  # not walkable, minable
            (BlockType.STONE, False, True),  # not walkable, minable
            (BlockType.COAL, False, True),  # not walkable, minable
            (BlockType.LAVA, False, False),  # not walkable, not minable
            (BlockType.DIAMOND, False, True),  # not walkable, minable
            (BlockType.WATER, False, False),  # not walkable, not minable
        ]

        for block_type, expected_walkable, expected_minable in test_cases:
            game_world.replace_block(0, 0, block_type)
            block = game_world.get_block(0, 0)

            assert (
                block.type.walkable == expected_walkable
            ), f"{block_type} walkable mismatch"
            assert block.type.minable == expected_minable, f"{block_type} minable mismatch"