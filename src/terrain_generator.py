"""
Configuration-driven terrain generator

This is an enhanced version of the terrain generator that uses the
configuration system to make it much easier to add new block types
and adjust distributions.
"""

import random
import noise
from terrain_config import TerrainConfig, DEFAULT_CONFIG
from block_type import BlockType
from typing import Optional


class ConfigurableTerrainGenerator:
    """Enhanced terrain generator driven by configuration"""

    def __init__(self, config: Optional[TerrainConfig] = None, seed=42):
        self.config: TerrainConfig = config or DEFAULT_CONFIG
        self.seed: int = seed

        # Validate configuration on initialization
        issues = self.config.validate_configuration()
        if issues:
            raise ValueError(f"Configuration validation failed: {issues}")

    def get_base_terrain_noise(self, world_x, world_y):
        """Generate base terrain noise value using configuration"""
        params = self.config.noise_params

        # Add large offset to avoid boring area around origin
        # This ensures the starting area has interesting terrain variation
        # Use prime numbers to ensure we get into more interesting noise areas
        offset_x = world_x + 10007.0
        offset_y = world_y + 10009.0

        # Large-scale terrain features (continents, oceans)
        large_scale = noise.pnoise2(
            offset_x * params["large_scale"]["scale"],
            offset_y * params["large_scale"]["scale"],
            octaves=params["large_scale"]["octaves"],
            persistence=params["large_scale"]["persistence"],
            lacunarity=params["large_scale"]["lacunarity"],
            base=self.seed,
        )

        # Medium-scale terrain features (biomes, regions)
        medium_scale = noise.pnoise2(
            offset_x * params["medium_scale"]["scale"],
            offset_y * params["medium_scale"]["scale"],
            octaves=params["medium_scale"]["octaves"],
            persistence=params["medium_scale"]["persistence"],
            lacunarity=params["medium_scale"]["lacunarity"],
            base=self.seed + 100,
        )

        # Small-scale height variation (local details)
        small_scale = noise.pnoise2(
            offset_x * params["small_scale"]["scale"],
            offset_y * params["small_scale"]["scale"],
            octaves=params["small_scale"]["octaves"],
            persistence=params["small_scale"]["persistence"],
            lacunarity=params["small_scale"]["lacunarity"],
            base=self.seed + 200,
        )

        # Weighted combination
        combined = 0.5 * large_scale + 0.3 * medium_scale + 0.2 * small_scale

        # Normalize to [0,1] range
        normalized = (combined + 1) / 2

        # Stretch the distribution to use full [0,1] range
        min_expected = params["noise_stretch_min"]
        max_expected = params["noise_stretch_max"]
        stretched = (normalized - min_expected) / (max_expected - min_expected)
        enhanced = max(0, min(1, stretched))  # Clamp to [0,1]

        return enhanced

    def get_base_terrain_type(self, world_x, world_y) -> BlockType:
        """Determine base terrain type using configuration"""
        noise_value = self.get_base_terrain_noise(world_x, world_y)

        # Find the appropriate terrain layer based on thresholds
        for layer in self.config.base_layers:
            if noise_value < layer.threshold:
                return layer.name

        # If no threshold matched, return the last layer
        return (
            self.config.base_layers[-1].name
            if self.config.base_layers
            else BlockType.STONE
        )

    def is_deep_underground(self, world_x, world_y):
        """Check if location is in deep underground area"""
        noise_value = self.get_base_terrain_noise(world_x, world_y)
        return noise_value >= self.config.noise_params["stone_threshold"]

    def get_feature_noise(self, world_x, world_y):
        """Generate 2D feature placement noise"""
        # Use same offset as base terrain for consistency
        offset_x = world_x + 10007.0
        offset_y = world_y + 10009.0

        return noise.pnoise2(
            offset_x * self.config.noise_params["feature_scale"],
            offset_y * self.config.noise_params["feature_scale"],
            octaves=3,
            persistence=0.6,
            lacunarity=2.0,
            base=self.seed + 1000,
        )

    def should_place_lava_pool(self, world_x, world_y):
        """Determine if lava should form a pool at this location"""
        if not self.is_deep_underground(world_x, world_y):
            return False

        # Use same offset as base terrain for consistency
        offset_x = world_x + 10007.0
        offset_y = world_y + 10009.0

        # Use different noise for lava pool formation
        lava_noise = noise.pnoise2(
            offset_x * self.config.noise_params["feature_scale"] * 0.5,
            offset_y * self.config.noise_params["feature_scale"] * 0.5,
            octaves=2,
            persistence=0.4,
            lacunarity=2.0,
            base=self.seed + 2000,
        )

        return lava_noise > self.config.noise_params["lava_pool_threshold"]

    def generate_block_type(self, world_x, world_y) -> BlockType:
        """Generate the final block type using configuration"""
        # Step 1: Get base terrain
        base_terrain = self.get_base_terrain_type(world_x, world_y)

        # Step 2: Get noise values for feature placement
        feature_noise = self.get_feature_noise(world_x, world_y)
        is_deep = self.is_deep_underground(world_x, world_y)

        # Seed random generator for consistent results
        random.seed(world_x * 10000 + world_y + self.seed)

        # Step 3: Process feature rules in order
        for rule in self.config.feature_rules:
            # Check if this rule applies to the current base terrain
            if base_terrain not in rule.base_terrain:
                continue

            # Check if deep underground requirement is met
            if rule.requires_deep and not is_deep:
                continue

            # Check noise threshold and spawn chance
            if (
                feature_noise > rule.noise_threshold
                and random.random() < rule.spawn_chance
            ):
                # Special case for lava pools
                if rule.name == BlockType.LAVA and rule.requires_deep:
                    if self.should_place_lava_pool(world_x, world_y):
                        return rule.name
                else:
                    return rule.name

        # No feature rule matched, return base terrain
        return base_terrain

    def update_configuration(self, config: TerrainConfig):
        """Update the configuration and validate it"""
        issues = config.validate_configuration()
        if issues:
            raise ValueError(f"Configuration validation failed: {issues}")
        self.config = config

    def get_configuration_summary(self):
        """Get a summary of the current configuration"""
        summary = {
            "base_layers": len(self.config.base_layers),
            "feature_rules": len(self.config.feature_rules),
            "target_distribution": self.config.get_target_distribution(),
            "validation_issues": self.config.validate_configuration(),
        }
        return summary


# Convenience function for backward compatibility
def create_terrain_generator(seed=42):
    """Create a terrain generator using the default configuration"""
    return ConfigurableTerrainGenerator(DEFAULT_CONFIG, seed)
