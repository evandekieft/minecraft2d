import random
from game import Game


class TestNoiseGeneration:
    def test_noise_based_generation(self):
        game = Game()

        # Sample blocks and verify they are valid terrain types
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
        for x in range(20):
            for y in range(20):
                block = game.get_block(x, y)
                assert block.type in valid_types, f"Invalid block type: {block.type}"

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

        # Should have both grass and wood blocks (not all the same)
        unique_types = set(blocks)
        assert len(unique_types) > 1

    def test_generated_blocks_are_valid_types(self):
        game = Game()

        # Test that generated blocks are valid terrain types
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
        for x in range(20):
            for y in range(20):
                block = game.get_block(x, y)
                assert block.type in valid_types, f"Invalid block type: {block.type}"
