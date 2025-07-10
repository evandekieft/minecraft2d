from game_world import GameWorld
from world_storage import WorldStorage
from unittest import mock
import pygame
from block_type import BlockType


def test_save_world():
    world = GameWorld()
    world_storage = WorldStorage()

    with mock.patch("json.dump") as mock_dump:
        assert world_storage.save_world(world, "test_name")
        mock_dump.assert_called_once()

        args, _ = mock_dump.call_args
        assert args[0]["world_name"] == "test_name"


def test_save_and_load_same_world(pygame_setup):
    world = GameWorld()
    world_storage = WorldStorage()
    screen = pygame.Surface((800, 600))

    # many draw time bugs from bad serialization
    # only surface with inventory items.
    world.player.add_to_inventory(BlockType.WOOD)

    with mock.patch("json.dump") as mock_dump:
        world_storage.save_world(world, "test_name")
        mock_dump.assert_called_once()
        args, _ = mock_dump.call_args
        dumped_dict = args[0]
        assert dumped_dict["world_name"] == "test_name"

        with mock.patch("json.load") as mock_load:
            mock_load.return_value = dumped_dict
            loaded_world = world_storage.load_world("test_name")
            assert len(loaded_world.chunks) == len(world.chunks)

            # ensure loaded world can be drawn without error
            loaded_world.draw(screen)
