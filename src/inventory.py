from typing import Dict, Optional
from block_type import BlockType


class Inventory:
    """Manages an inventory of blocks on behalf of the player."""

    def __init__(
        self, inventory: Optional[Dict[BlockType, int]] = None, active_slot: int = 0
    ):
        self.inventory = inventory or {}
        self.active_slot = active_slot

    def add(self, block_type: BlockType):
        if block_type in self.inventory:
            self.inventory[block_type] += 1
        else:
            self.inventory[block_type] = 1

    def remove(self, block_type: BlockType):
        # Remove one from inventory
        self.inventory[block_type] -= 1
        # Remove the block type entirely if count reaches 0
        if self.inventory[block_type] == 0:
            del self.inventory[block_type]

    def get_top_inventory_items(self, count=5):
        # Get items in stable order (insertion order)
        items = list(self.inventory.items())
        return items[:count]

    def get_active_block_type(self) -> Optional[BlockType]:
        # Get the block type in the active slot
        top_items = self.get_top_inventory_items()
        if 0 <= self.active_slot < len(top_items):
            return top_items[self.active_slot][0]
        return None

    def set_active_slot(self, slot: int):
        self.active_slot = slot

    def has_block_type(self, type: BlockType):
        return type in self.inventory and self.inventory[type] > 0

    def get_item_count(self, block_type: BlockType):
        return self.inventory.get(block_type, 0)
