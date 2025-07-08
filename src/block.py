from constants import (
    GREEN,
    LIGHT_BROWN,
    DARK_BROWN,
    BLUE,
    WHITE,
    BRIGHT_BLUE,
    RED,
    BLACK,
    SAND_COLOR,
    GRAY,
)


class Block:
    def __init__(self, block_type):
        self.type = block_type
        self.walkable = self._get_walkable(block_type)
        self.color = self._get_color(block_type)
        self.minable = self._get_minable(block_type)
        self.mining_difficulty = self._get_mining_difficulty(block_type)
        self.max_health = self.mining_difficulty
        self.current_health = self.max_health

    def _get_walkable(self, block_type):
        walkable_blocks = {"grass", "dirt", "sand"}
        return block_type in walkable_blocks

    def _get_color(self, block_type):
        colors = {
            "grass": GREEN,
            "dirt": DARK_BROWN,
            "sand": SAND_COLOR,
            "wood": LIGHT_BROWN,
            "stone": GRAY,
            "coal": BLACK,
            "lava": RED,
            "diamond": BRIGHT_BLUE,
            "water": BLUE,
        }
        return colors.get(block_type, WHITE)

    def _get_minable(self, block_type):
        minable_blocks = {"wood", "stone", "diamond", "coal"}
        return block_type in minable_blocks

    def _get_mining_difficulty(self, block_type):
        # Mining difficulty in health points (higher = takes longer)
        difficulties = {
            "wood": 1.5,  # 1.5 seconds with bare hands (twice as fast as before)
            "stone": 5.0,  # 5 seconds with bare hands
            "coal": 4.0,  # 4 seconds with bare hands
            "diamond": 8.0,  # 8 seconds with bare hands (very hard)
        }
        return difficulties.get(block_type, 1.0)

    def reset_health(self):
        """Reset block health to maximum (when mining is interrupted)"""
        self.current_health = self.max_health

    def take_damage(self, damage):
        """Apply mining damage to the block. Returns True if block is destroyed."""
        if not self.minable:
            return False

        self.current_health -= damage
        return self.current_health <= 0

    def get_mining_result(self):
        """Get the item(s) that should be added to inventory when this block is mined"""
        mining_results = {
            "wood": "wood",
            "stone": "stone",
            "coal": "coal",
            "diamond": "diamond",
        }
        return mining_results.get(self.type, None)

    def get_replacement_block(self):
        """Get the block type that should replace this block when mined"""
        replacements = {
            "wood": "grass",  # Wood becomes grass when mined
            "stone": "dirt",  # Stone becomes dirt when mined
            "coal": "dirt",  # Coal becomes dirt when mined
            "diamond": "dirt",  # Diamond becomes dirt when mined
        }
        return replacements.get(self.type, self.type)
