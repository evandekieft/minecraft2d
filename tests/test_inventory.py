from inventory import Inventory
from block_type import BlockType


class TestInventory:
    def test_inventory_initialization(self):
        inventory = Inventory()
        assert inventory.inventory == {}
        assert inventory.active_slot == 0

    def test_add_to_inventory_new_item(self):
        inventory = Inventory()
        inventory.add(BlockType.WOOD)

        assert inventory.inventory[BlockType.WOOD] == 1

    def test_add_to_inventory_existing_item(self):
        inventory = Inventory()
        inventory.add(BlockType.WOOD)
        inventory.add(BlockType.WOOD)

        assert inventory.inventory[BlockType.WOOD] == 2

    def test_add_multiple_item_types(self):
        inventory = Inventory()
        inventory.add(BlockType.WOOD)
        inventory.add(BlockType.WOOD)
        inventory.add(BlockType.GRASS)

        assert inventory.inventory[BlockType.WOOD] == 2
        assert inventory.inventory[BlockType.GRASS] == 1

    def test_get_top_inventory_items_empty(self):
        inventory = Inventory()
        top_items = inventory.get_top_inventory_items(5)

        assert top_items == []

    def test_get_top_inventory_items_sorted(self):
        inventory = Inventory()
        inventory.add(BlockType.WOOD)
        inventory.add(BlockType.GRASS)
        inventory.add(BlockType.GRASS)
        inventory.add(BlockType.GRASS)
        inventory.add(BlockType.GRASS)

        top_items = inventory.get_top_inventory_items(5)

        assert top_items == [(BlockType.WOOD, 1), (BlockType.GRASS, 4)]

    def test_get_active_block_type_empty(self):
        inventory = Inventory()
        assert inventory.get_active_block_type() is None

    def test_get_active_block_type_valid(self):
        inventory = Inventory()
        inventory.add(BlockType.WOOD)
        inventory.add(BlockType.GRASS)
        inventory.active_slot = 0

        assert inventory.get_active_block_type() == BlockType.WOOD

    def test_get_active_block_type_out_of_range(self):
        inventory = Inventory()
        inventory.add(BlockType.WOOD)
        inventory.active_slot = 5

        assert inventory.get_active_block_type() is None
