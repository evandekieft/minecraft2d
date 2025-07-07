# Perlin Noise Terrain Generation

This document describes the new Perlin noise-based terrain generation system implemented for the 2D Minecraft game.

## Overview

The terrain generation system uses multiple layers of Perlin noise to create realistic and diverse landscapes with proper resource distribution. The system generates 9 different block types following geological principles.

## System Architecture

### TerrainGenerator Class

The `TerrainGenerator` class in `world.py` handles all terrain generation logic:

```python
# Initialize with customizable parameters
generator = TerrainGenerator(seed=42)
```

### Two-Layer Noise System

#### Layer 1: Base Terrain (1D + 2D Hybrid)
Creates the fundamental landscape using three noise scales:
- **Large-scale** (0.005): Continental features and major terrain zones
- **Medium-scale** (0.02): Regional terrain variation
- **Small-scale** (0.1, 0.05): Local height variation and detail

#### Layer 2: Feature Placement (2D)
Places surface features and resources based on terrain type and additional noise patterns.

## Block Types and Distribution

### Terrain Types (by elevation/noise value)
1. **Water** (0-30%): Low-lying areas, forms lakes and rivers
2. **Sand** (30-40%): Transitional areas around water bodies
3. **Grass** (40-70%): Primary surface terrain, most common
4. **Stone** (70-85%): Higher elevation areas and underground
5. **Deep Stone** (85-100%): Deepest underground areas

### Resource Distribution Rules

#### Wood 🌳
- **Appears on**: Grass and dirt only
- **Density**: 8% chance
- **Purpose**: Building material, appears as surface trees

#### Coal ⚫
- **Appears on**: Any stone (surface or deep)
- **Density**: 15% chance
- **Purpose**: Fuel and crafting material

#### Lava 🔥
- **Appears on**: Deep underground stone only (noise ≥ 0.85)
- **Density**: 8% base chance + lava pool formation
- **Special**: Forms pools using dedicated noise layer
- **Purpose**: Dangerous obstacle, potential energy source

#### Diamond 💎
- **Appears on**: Deep underground stone only (noise ≥ 0.85)
- **Density**: 3% chance (rarest resource)
- **Purpose**: High-value rare material

## Customizable Parameters

All generation parameters can be easily adjusted in the `TerrainGenerator.__init__()` method:

```python
# Noise scales (smaller = larger features)
self.terrain_scale = 0.01
self.feature_scale = 0.05
self.height_scale = 0.008

# Terrain thresholds
self.water_threshold = 0.30
self.sand_threshold = 0.40
self.grass_threshold = 0.60
self.stone_threshold = 0.75

# Resource densities
self.wood_density = 0.08
self.coal_density = 0.15
self.lava_density = 0.08
self.diamond_density = 0.03
```

## Visualization and Testing

### Visualization Script
Use `visualize_terrain.py` to generate and visualize terrain maps:

```bash
# Basic usage
python visualize_terrain.py

# Custom parameters
python visualize_terrain.py --width 800 --height 600 --seed 42 --save map.png

# Different world regions
python visualize_terrain.py --center-x 1000 --center-y 500
```

### Example Terrain Statistics
Typical distribution from a 400×300 map:
- **Grass**: ~72% (primary terrain)
- **Sand**: ~13% (coastal/transitional)
- **Stone**: ~12% (elevated/underground)
- **Water**: ~2% (lakes/rivers)
- **Coal**: ~0.1% (resource)
- **Wood**: ~0.1% (surface features)
- **Lava**: <0.1% (rare, deep only)
- **Diamond**: <0.1% (very rare, deep only)

## Integration with Game Systems

### Mining System
- All minable blocks (wood, stone, coal, diamond) work with existing mining mechanics
- Block replacement follows geological logic (coal/diamond → dirt when mined)

### Movement System
- Walkability rules maintained (only grass, dirt, sand are walkable)
- Water and lava act as obstacles
- Stone, coal, diamond, and wood block player movement

### Inventory System
- All mineable resources can be collected and stored
- Resource rarity affects game balance naturally

## Seed-Based Generation

The system uses deterministic seed-based generation ensuring:
- **Consistency**: Same seed always produces identical terrain
- **Multiplayer compatibility**: All players see the same world
- **Chunk-based loading**: Terrain generates on-demand as players explore

## Performance Considerations

- **Efficient chunk generation**: Only generates visible areas
- **Cached calculations**: Noise values computed once per coordinate
- **Scalable architecture**: Handles infinite world exploration

## Future Expansion Ideas

The modular design supports easy addition of:
- **Biomes**: Different parameter sets for desert, forest, mountain regions
- **Ore veins**: Clustered resource deposits using additional noise layers
- **Cave systems**: Underground hollow areas using 3D noise
- **Structures**: Villages, dungeons using feature placement logic
- **Seasonal variation**: Time-based parameter modification