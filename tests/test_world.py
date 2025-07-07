import pytest
import random
from world import Game, Block


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
        assert game.get_block(0, 0) is not None    # Chunk (0, 0)
        assert game.get_block(15, 15) is not None  # Chunk (0, 0)
        assert game.get_block(16, 16) is not None  # Chunk (1, 1)
        assert game.get_block(-1, -1) is not None  # Chunk (-1, -1)

    def test_negative_coordinates(self):
        game = Game()
        
        # Test negative world coordinates
        block = game.get_block(-10, -10)
        assert block is not None
        assert block.type in ["grass", "tree"]

    def test_block_type_distribution(self):
        game = Game()
        
        # Sample many blocks to verify distribution
        block_types = []
        for x in range(100):
            for y in range(100):
                block = game.get_block(x, y)
                block_types.append(block.type)
        
        grass_count = block_types.count("grass")
        tree_count = block_types.count("tree")
        
        # Should be roughly 90% grass, 10% trees
        total = len(block_types)
        grass_ratio = grass_count / total
        tree_ratio = tree_count / total
        
        assert 0.85 < grass_ratio < 0.95
        assert 0.05 < tree_ratio < 0.15

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


class TestBlockGeneration:
    def test_only_grass_and_trees_generated(self):
        game = Game()
        
        # Sample blocks and verify only grass and trees (current generation)
        for x in range(20):
            for y in range(20):
                block = game.get_block(x, y)
                assert block.type in ["grass", "tree"]

    def test_block_generation_deterministic(self):
        # Test that the same seed produces the same block
        random.seed(42)
        prob1 = random.random()
        
        random.seed(42)
        prob2 = random.random()
        
        assert prob1 == prob2

    def test_different_coordinates_different_blocks(self):
        game = Game()
        
        # Get a sample of blocks
        blocks = []
        for x in range(10):
            for y in range(10):
                block = game.get_block(x, y)
                blocks.append(block.type)
        
        # Should have both grass and trees (not all the same)
        unique_types = set(blocks)
        assert len(unique_types) > 1

    def test_generated_blocks_are_valid_types(self):
        game = Game()
        
        # Test that generated blocks are only the expected types
        for x in range(20):
            for y in range(20):
                block = game.get_block(x, y)
                # Current generation only creates grass and tree blocks
                assert block.type in ["grass", "tree"], f"Unexpected block type: {block.type}"


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
            ("sand", True, False),    # walkable, not minable
            ("wood", False, True),    # not walkable, minable
            ("stone", False, True),   # not walkable, minable
            ("coal", False, True),    # not walkable, minable
            ("lava", False, False),   # not walkable, not minable
            ("diamond", False, True), # not walkable, minable
            ("water", False, False),  # not walkable, not minable
        ]
        
        for block_type, expected_walkable, expected_minable in test_cases:
            game.replace_block(0, 0, block_type)
            block = game.get_block(0, 0)
            
            assert block.walkable == expected_walkable, f"{block_type} walkable mismatch"
            assert block.minable == expected_minable, f"{block_type} minable mismatch"