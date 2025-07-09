"""
Configuration-driven terrain generation system

This module provides a flexible, data-driven approach to terrain generation
that makes it easy to add new block types, adjust distributions, and test
different configurations without modifying core logic.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
import random
import noise
from block_type import BlockType


@dataclass
class TerrainLayer:
    """Configuration for a base terrain layer"""

    name: BlockType
    threshold: float  # Noise value threshold (0-1)
    target_percentage: float  # Desired percentage of terrain
    description: str = ""


@dataclass
class FeatureRule:
    """Configuration for a terrain feature (blocks that spawn on base terrain)"""

    name: BlockType
    base_terrain: List[BlockType]  # Which base terrain types this can spawn on
    spawn_chance: float  # Probability (0-1) of spawning
    noise_threshold: float  # Minimum noise value required
    requires_deep: bool = False  # Whether this requires deep underground areas
    target_percentage: float = 0.0  # Desired percentage of terrain
    description: str = ""


class TerrainConfig:
    """Complete terrain generation configuration"""

    def __init__(self):
        # Base terrain layers (ordered by noise threshold)
        self.base_layers = [
            TerrainLayer(BlockType.WATER, 0.25, 25.0, "Water in low-lying areas"),
            TerrainLayer(BlockType.SAND, 0.35, 10.0, "Sand beaches around water"),
            TerrainLayer(BlockType.GRASS, 0.70, 35.0, "Grass fields and plains"),
            TerrainLayer(BlockType.STONE, 0.84, 14.0, "Stone mountains and hills"),
        ]

        # Feature rules (processed in order)
        self.feature_rules = [
            FeatureRule(
                BlockType.WOOD,
                [BlockType.GRASS, BlockType.DIRT],
                0.75,
                0.3,
                False,
                10.0,
                "Trees on grass/dirt",
            ),
            FeatureRule(
                BlockType.LAVA,
                [BlockType.STONE],
                0.80,
                0.4,
                True,
                5.0,
                "Lava in deep areas",
            ),
            FeatureRule(
                BlockType.DIAMOND,
                [BlockType.STONE],
                0.30,
                0.6,
                True,
                1.0,
                "Rare diamonds deep underground",
            ),
            FeatureRule(
                BlockType.COAL,
                [BlockType.STONE],
                0.15,
                0.2,
                False,
                0.0,
                "Coal in stone areas",
            ),
        ]

        # Noise generation parameters
        self.noise_params = {
            "large_scale": {
                "scale": 0.002,
                "octaves": 3,
                "persistence": 0.5,
                "lacunarity": 2.0,
            },
            "medium_scale": {
                "scale": 0.01,
                "octaves": 4,
                "persistence": 0.6,
                "lacunarity": 2.0,
            },
            "small_scale": {
                "scale": 0.05,
                "octaves": 2,
                "persistence": 0.3,
                "lacunarity": 2.0,
            },
            "feature_scale": 0.05,
            "noise_stretch_min": 0.35,
            "noise_stretch_max": 0.65,
            "stone_threshold": 0.84,  # Threshold for "deep underground"
            "lava_pool_threshold": 0.2,
        }

    def get_target_distribution(self) -> Dict[BlockType, float]:
        """Get the target distribution for all terrain types"""
        distribution = {}

        # Add base terrain targets
        for layer in self.base_layers:
            distribution[layer.name] = layer.target_percentage

        # Add feature targets
        for rule in self.feature_rules:
            if rule.target_percentage > 0:
                distribution[rule.name] = rule.target_percentage

        return distribution

    def get_base_layer_by_name(self, name: str) -> Optional[TerrainLayer]:
        """Get a base terrain layer by name"""
        for layer in self.base_layers:
            if layer.name == name:
                return layer
        return None

    def get_feature_rule_by_name(self, name: str) -> Optional[FeatureRule]:
        """Get a feature rule by name"""
        for rule in self.feature_rules:
            if rule.name == name:
                return rule
        return None

    def auto_adjust_thresholds(
        self, actual_distribution: Dict[BlockType, Dict[str, float]]
    ):
        """
        Automatically adjust thresholds based on actual vs target distribution

        Args:
            actual_distribution: Dict with format {BlockType: {'percentage': float}}
        """
        print("Auto-adjusting thresholds based on actual distribution...")

        # Simple heuristic: if actual > target, increase threshold; if actual < target, decrease threshold
        adjustment_factor = 0.05  # How much to adjust per iteration

        for layer in self.base_layers:
            if layer.name in actual_distribution:
                actual_pct = actual_distribution[layer.name]["percentage"]
                target_pct = layer.target_percentage
                difference = actual_pct - target_pct

                if abs(difference) > 2.0:  # Only adjust if difference is significant
                    # If we have too much of this terrain, increase threshold
                    # If we have too little, decrease threshold
                    adjustment = adjustment_factor * (difference / target_pct)
                    layer.threshold += adjustment
                    layer.threshold = max(
                        0.1, min(0.9, layer.threshold)
                    )  # Clamp to reasonable range

                    print(
                        f"  {layer.name.value}: {actual_pct:.1f}% -> {target_pct:.1f}% (threshold: {layer.threshold:.3f})"
                    )

    def validate_configuration(self) -> List[str]:
        """Validate the configuration and return any issues"""
        issues = []

        # Check that base layer thresholds are in ascending order
        for i in range(1, len(self.base_layers)):
            if self.base_layers[i].threshold <= self.base_layers[i - 1].threshold:
                issues.append(
                    f"Base layer thresholds must be in ascending order: {self.base_layers[i-1].name} -> {self.base_layers[i].name}"
                )

        # Check that all feature rules reference valid base terrain
        base_terrain_names = {layer.name for layer in self.base_layers}
        for rule in self.feature_rules:
            for base_name in rule.base_terrain:
                if (
                    base_name not in base_terrain_names and base_name != BlockType.DIRT
                ):  # dirt is a special case
                    issues.append(
                        f"Feature rule '{rule.name.value}' references unknown base terrain '{base_name.value}'"
                    )

        # Check that target percentages are reasonable
        total_base_target = sum(layer.target_percentage for layer in self.base_layers)
        total_feature_target = sum(
            rule.target_percentage for rule in self.feature_rules
        )

        if total_base_target > 100:
            issues.append(
                f"Base terrain target percentages sum to {total_base_target}%, which exceeds 100%"
            )

        if total_base_target + total_feature_target > 100:
            issues.append(
                f"Total target percentages sum to {total_base_target + total_feature_target}%, which exceeds 100%"
            )

        return issues


# Default configuration instance
DEFAULT_CONFIG = TerrainConfig()
