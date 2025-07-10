import json
import os
from game_world import GameWorld
from inventory import Inventory
from block import Block
from block_type import BlockType


class WorldStorage:
    def __init__(self):
        self.saves_dir = "saves"
        self.ensure_saves_directory()

    def ensure_saves_directory(self):
        """Create saves directory if it doesn't exist"""
        if not os.path.exists(self.saves_dir):
            os.makedirs(self.saves_dir)

    def save_world(self, world: GameWorld, world_name: str):
        """Save the current game state to a file"""

        inventory = {k.value: v for k, v in world.player.inventory.inventory.items()}
        # Prepare world data
        world_data = {
            "world_name": world_name,
            "player": {
                "world_x": world.player.world_x,
                "world_y": world.player.world_y,
                "orientation": world.player.orientation,
                "inventory": inventory,
                "active_slot": world.player.inventory.active_slot,
            },
            "chunks": {},
            "terrain_seed": world.terrain_generator.seed,
        }

        # Save chunks
        for (chunk_x, chunk_y), chunk in world.chunks.items():
            chunk_key = f"{chunk_x},{chunk_y}"
            chunk_data = {}

            for (local_x, local_y), block in chunk.items():
                block_key = f"{local_x},{local_y}"
                chunk_data[block_key] = {
                    "type": block.type.value,  # Save as string value
                    "current_health": block.current_health,
                }

            world_data["chunks"][chunk_key] = chunk_data

        # Write to file
        filepath = os.path.join(self.saves_dir, f"{world_name}.json")
        with open(filepath, "w") as f:
            json.dump(world_data, f, indent=2)

        return True

    def load_world(self, world_name: str) -> GameWorld:
        """Load a world from file and return a GameWorld instance"""

        filepath = os.path.join(self.saves_dir, f"{world_name}.json")
        with open(filepath, "r") as f:
            world_data = json.load(f)

        # Create new game world instance
        terrain_seed = world_data.get("terrain_seed", 42)
        game = GameWorld(terrain_seed=terrain_seed)

        # Restore player state
        player_data = world_data.get("player", {})
        game.player.world_x = player_data.get("world_x", 0)
        game.player.world_y = player_data.get("world_y", 0)
        game.player.orientation = player_data.get("orientation", "north")

        stored_inventory = player_data.get("inventory", {})
        stored_active_slot = player_data.get("active_slot", 0)

        game.player.inventory = Inventory(
            {BlockType(k): v for k, v in stored_inventory.items()}, stored_active_slot
        )

        # Clear auto-generated chunks and load saved ones
        game.chunks = {}

        # Restore chunks
        chunks_data = world_data.get("chunks", {})
        for chunk_key, chunk_data in chunks_data.items():
            chunk_x, chunk_y = map(int, chunk_key.split(","))
            chunk = {}

            for block_key, block_data in chunk_data.items():
                local_x, local_y = map(int, block_key.split(","))
                # Convert string back to BlockType enum
                block_type_str = block_data["type"]
                block_type = BlockType(block_type_str)
                block = Block(block_type)
                block.current_health = block_data["current_health"]
                chunk[(local_x, local_y)] = block

            game.chunks[(chunk_x, chunk_y)] = chunk

        # Generate any missing chunks around player
        game._generate_chunks_around_player()

        return game

    def delete_world(self, world_name: str):
        """Delete a world save file"""

        filepath = os.path.join(self.saves_dir, f"{world_name}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    def get_world_list(self):
        """Get list of saved worlds by name"""
        worlds = []

        if os.path.exists(self.saves_dir):
            for filename in os.listdir(self.saves_dir):
                if filename.endswith(".json"):
                    world_name = filename[:-5]  # Remove .json extension
                    worlds.append(world_name)

        return sorted(worlds)

    def world_exists(self, world_name: str):
        """Check if a world save file exists"""
        filepath = os.path.join(self.saves_dir, f"{world_name}.json")
        return os.path.exists(filepath)

    def create_new_world_unsaved(self, terrain_seed=None):
        """Create a new world without saving it (no name yet)"""

        if terrain_seed is None:
            import random

            terrain_seed = random.randint(1, 1000000)

        # Create new game world instance
        game = GameWorld(terrain_seed=terrain_seed)
        return game
