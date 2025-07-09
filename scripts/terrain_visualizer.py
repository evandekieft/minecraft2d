#!/usr/bin/env python3
"""
Terrain Visualization Script

This script generates and visualizes the Perlin noise-based terrain
for the 2D Minecraft game. It creates a map showing different block types
with distinct colors, helping to tune terrain generation parameters.

Usage:
    python visualize_terrain.py [--width WIDTH] [--height HEIGHT] [--seed SEED]
"""

import argparse
import matplotlib.pyplot as plt
import numpy as np
from terrain_generator import ConfigurableTerrainGenerator, create_terrain_generator

# Color mapping for visualization (RGB values)
BLOCK_COLORS = {
    "water": (0.0, 0.4, 0.8),  # Blue
    "sand": (0.9, 0.8, 0.6),  # Sandy beige
    "grass": (0.2, 0.8, 0.2),  # Green
    "dirt": (0.4, 0.2, 0.1),  # Brown
    "stone": (0.5, 0.5, 0.5),  # Gray
    "wood": (0.6, 0.4, 0.2),  # Light brown
    "coal": (0.1, 0.1, 0.1),  # Black
    "lava": (1.0, 0.2, 0.0),  # Red
    "diamond": (0.0, 0.8, 1.0),  # Bright blue
}


def generate_terrain_map(width, height, seed=42, center_x=0, center_y=0):
    """Generate a terrain map of the specified size"""
    print(f"Generating {width}x{height} terrain map with seed {seed}...")

    # Initialize terrain generator
    terrain_gen: ConfigurableTerrainGenerator = create_terrain_generator(seed=seed)

    # Create arrays to store the map data
    terrain_map = np.zeros((height, width), dtype=object)
    color_map = np.zeros((height, width, 3))

    # Generate terrain for each position
    for y in range(height):
        for x in range(width):
            # Calculate world coordinates (centered around center_x, center_y)
            world_x = center_x + x - width // 2
            world_y = center_y + y - height // 2

            # Generate block type
            block_type = terrain_gen.generate_block_type(world_x, world_y)
            terrain_map[y, x] = block_type
            color_map[y, x] = block_type.color

    return terrain_map, color_map


def calculate_terrain_stats(terrain_map):
    """Calculate statistics about the generated terrain"""
    height, width = terrain_map.shape
    total_blocks = height * width

    # Count block types
    block_counts = {}
    for y in range(height):
        for x in range(width):
            block_type = terrain_map[y, x]
            block_counts[block_type] = block_counts.get(block_type, 0) + 1

    # Calculate percentages and create results dictionary
    stats = {}
    for block_type, count in block_counts.items():
        percentage = (count / total_blocks) * 100
        stats[block_type] = {"count": count, "percentage": percentage}

    return stats, total_blocks


def print_terrain_stats(terrain_map):
    """Print statistics about the generated terrain"""
    height, width = terrain_map.shape
    stats, total_blocks = calculate_terrain_stats(terrain_map)

    print(f"\nTerrain Statistics ({width}x{height} = {total_blocks} blocks):")
    print("-" * 50)

    # Sort by count (descending)
    sorted_blocks = sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True)

    for block_type, data in sorted_blocks:
        print(
            f"{block_type:>8}: {data['count']:>6} blocks ({data['percentage']:5.1f}%)"
        )


def compare_to_target(terrain_map, target_distribution):
    """Compare actual terrain distribution to target distribution"""
    stats, total_blocks = calculate_terrain_stats(terrain_map)

    print(f"\nTarget vs Actual Distribution:")
    print("-" * 50)
    print(f"{'Block Type':>8} | {'Target':>6} | {'Actual':>6} | {'Diff':>6}")
    print("-" * 50)

    for block_type, target_pct in target_distribution.items():
        actual_pct = stats.get(block_type, {"percentage": 0})["percentage"]
        diff = actual_pct - target_pct
        print(
            f"{block_type:>8} | {target_pct:>5.1f}% | {actual_pct:>5.1f}% | {diff:>+5.1f}%"
        )

    # Check for any block types not in target
    for block_type in stats:
        if block_type not in target_distribution:
            actual_pct = stats[block_type]["percentage"]
            print(f"{block_type:>8} | {'N/A':>6} | {actual_pct:>5.1f}% | {'N/A':>6}")


def visualize_terrain(terrain_map, color_map, title="Terrain Map", save_path=None):
    """Create and display a visualization of the terrain"""
    height, width = terrain_map.shape

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))

    # Display the terrain
    ax.imshow(color_map, origin="upper", interpolation="nearest")

    # Customize the plot
    ax.set_title(title, fontsize=16, fontweight="bold")
    ax.set_xlabel("X Coordinate", fontsize=12)
    ax.set_ylabel("Y Coordinate", fontsize=12)

    # Add grid for better readability
    ax.grid(True, alpha=0.3, linewidth=0.5)

    # Create legend
    legend_elements = []
    for block_type, color in BLOCK_COLORS.items():
        if block_type in [
            terrain_map[y, x] for y in range(height) for x in range(width)
        ]:
            legend_elements.append(
                plt.Rectangle((0, 0), 1, 1, facecolor=color, label=block_type.title())
            )

    ax.legend(handles=legend_elements, loc="center left", bbox_to_anchor=(1, 0.5))

    # Adjust layout to prevent legend cutoff
    plt.tight_layout()

    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Map saved to: {save_path}")

    # Show the plot
    plt.show()


def main():
    """Main function to handle command line arguments and generate visualization"""
    parser = argparse.ArgumentParser(
        description="Visualize Perlin noise terrain generation"
    )
    parser.add_argument(
        "--width", type=int, default=200, help="Map width in blocks (default: 200)"
    )
    parser.add_argument(
        "--height", type=int, default=150, help="Map height in blocks (default: 150)"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for generation (default: 42)"
    )
    parser.add_argument(
        "--center-x", type=int, default=0, help="Center X coordinate (default: 0)"
    )
    parser.add_argument(
        "--center-y", type=int, default=0, help="Center Y coordinate (default: 0)"
    )
    parser.add_argument(
        "--save", type=str, help="Save map to file (e.g., terrain_map.png)"
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Don't display the map (useful with --save)",
    )
    parser.add_argument(
        "--compare-target",
        action="store_true",
        help="Compare actual distribution to target distribution",
    )

    args = parser.parse_args()

    # Define target distribution
    target_distribution = {
        "grass": 35.0,
        "water": 25.0,
        "sand": 10.0,
        "stone": 14.0,
        "wood": 10.0,
        "lava": 5.0,
        "diamond": 1.0,
    }

    # Generate terrain map
    terrain_map, color_map = generate_terrain_map(
        width=args.width,
        height=args.height,
        seed=args.seed,
        center_x=args.center_x,
        center_y=args.center_y,
    )

    # Print statistics
    print_terrain_stats(terrain_map)

    # Compare to target if requested
    if args.compare_target:
        compare_to_target(terrain_map, target_distribution)

    # Create visualization
    title = f"Terrain Map (Seed: {args.seed}, Size: {args.width}x{args.height})"

    if not args.no_display:
        visualize_terrain(terrain_map, color_map, title=title, save_path=args.save)
    elif args.save:
        # Save without displaying
        import matplotlib

        matplotlib.use("Agg")  # Use non-interactive backend
        visualize_terrain(terrain_map, color_map, title=title, save_path=args.save)


if __name__ == "__main__":
    main()
