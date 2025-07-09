import json
import os
from game_world import GameWorld
from inventory import Inventory
from block import Block
from block_type import BlockType


class WorldManager:
    def __init__(self):
        self.saves_dir = "saves"
        self.ensure_saves_directory()

    def ensure_saves_directory(self):
        """Create saves directory if it doesn't exist"""
        if not os.path.exists(self.saves_dir):
            os.makedirs(self.saves_dir)

    def save_world(self, game, world_name):
        """Save the current game state to a file"""
        try:
            # Prepare world data
            world_data = {
                "world_name": world_name,
                "player": {
                    "world_x": game.player.world_x,
                    "world_y": game.player.world_y,
                    "orientation": game.player.orientation,
                    "inventory": game.player.inventory.inventory,
                    "active_slot": game.player.inventory.active_slot,
                },
                "chunks": {},
                "terrain_seed": game.terrain_generator.seed,
                "day_time": getattr(
                    game, "day_time", 300.0
                ),  # Default to noon if not present
            }

            # Save chunks
            for (chunk_x, chunk_y), chunk in game.chunks.items():
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
        except Exception as e:
            print(f"Error saving world: {e}")
            return False

    def load_world(self, world_name):
        """Load a world from file and return a GameWorld instance"""
        try:
            filepath = os.path.join(self.saves_dir, f"{world_name}.json")

            if not os.path.exists(filepath):
                return None

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
            game.player.inventory = Inventory(
                player_data.get("inventory", {}), player_data.get("active_slot", 0)
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

        except Exception as e:
            print(f"Error loading world: {e}")
            return None

    def create_new_world(self, world_name, terrain_seed=None):
        """Create a new world with the given name"""
        try:
            if terrain_seed is None:
                import random

                terrain_seed = random.randint(1, 1000000)

            # Create new game world instance
            game = GameWorld(terrain_seed=terrain_seed)

            # Save the initial world state
            if self.save_world(game, world_name):
                return game
            else:
                return None

        except Exception as e:
            print(f"Error creating world: {e}")
            return None

    def create_new_world_unsaved(self, terrain_seed=None):
        """Create a new world without saving it (no name yet)"""
        try:
            if terrain_seed is None:
                import random

                terrain_seed = random.randint(1, 1000000)

            # Create new game world instance
            game = GameWorld(terrain_seed=terrain_seed)
            return game

        except Exception as e:
            print(f"Error creating world: {e}")
            return None

    def delete_world(self, world_name):
        """Delete a world save file"""
        try:
            filepath = os.path.join(self.saves_dir, f"{world_name}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Error deleting world: {e}")
            return False

    def get_world_list(self):
        """Get list of saved worlds"""
        worlds = []
        try:
            if os.path.exists(self.saves_dir):
                for filename in os.listdir(self.saves_dir):
                    if filename.endswith(".json"):
                        world_name = filename[:-5]  # Remove .json extension
                        worlds.append(world_name)
        except Exception as e:
            print(f"Error listing worlds: {e}")

        return sorted(worlds)

    def world_exists(self, world_name):
        """Check if a world save file exists"""
        filepath = os.path.join(self.saves_dir, f"{world_name}.json")
        return os.path.exists(filepath)
