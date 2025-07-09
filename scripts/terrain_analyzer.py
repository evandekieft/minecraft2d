#!/usr/bin/env python3
"""
Advanced Terrain Analysis Tool

This script provides comprehensive analysis and tuning capabilities for
terrain generation, making it much easier to develop and balance new
terrain configurations.
"""

import argparse

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from terrain_config import TerrainConfig, DEFAULT_CONFIG
from terrain_visualizer import generate_terrain_map, calculate_terrain_stats


class TerrainAnalyzer:
    """Advanced terrain analysis and tuning tool"""

    def __init__(self, config: TerrainConfig = None):
        self.config = config or DEFAULT_CONFIG
        self.results_history = []

    def analyze_distribution(self, width=200, height=150, seed=42, iterations=1):
        """
        Analyze terrain distribution over multiple iterations

        Args:
            width, height: Map dimensions
            seed: Random seed
            iterations: Number of maps to generate and average
        """
        print(f"Analyzing terrain distribution over {iterations} iteration(s)...")

        all_stats = []

        for i in range(iterations):
            current_seed = seed + i
            terrain_map, _ = generate_terrain_map(width, height, current_seed)
            stats, total_blocks = calculate_terrain_stats(terrain_map)
            all_stats.append(stats)

            if iterations > 1:
                print(f"  Iteration {i+1}/{iterations} complete")

        # Average the results
        averaged_stats = self._average_stats(all_stats)

        # Store results
        result = {
            "config_snapshot": self._serialize_config(),
            "stats": averaged_stats,
            "total_blocks": width * height,
            "parameters": {
                "width": width,
                "height": height,
                "seed": seed,
                "iterations": iterations,
            },
        }

        self.results_history.append(result)
        return result

    def _average_stats(self, stats_list):
        """Average statistics across multiple runs"""
        if len(stats_list) == 1:
            return stats_list[0]

        # Collect all block types
        all_block_types = set()
        for stats in stats_list:
            all_block_types.update(stats.keys())

        # Average each block type
        averaged = {}
        for block_type in all_block_types:
            counts = [
                stats.get(block_type, {"count": 0, "percentage": 0.0})["count"]
                for stats in stats_list
            ]
            percentages = [
                stats.get(block_type, {"count": 0, "percentage": 0.0})["percentage"]
                for stats in stats_list
            ]

            averaged[block_type] = {
                "count": sum(counts) / len(counts),
                "percentage": sum(percentages) / len(percentages),
            }

        return averaged

    def compare_to_target(self, stats):
        """Compare actual distribution to target"""
        target_distribution = self.config.get_target_distribution()

        print(f"\nTarget vs Actual Distribution:")
        print("-" * 60)
        print(
            f"{'Block Type':>12} | {'Target':>8} | {'Actual':>8} | {'Diff':>8} | {'Status'}"
        )
        print("-" * 60)

        total_error = 0
        for block_type, target_pct in target_distribution.items():
            actual_pct = stats.get(block_type, {"percentage": 0})["percentage"]
            diff = actual_pct - target_pct
            total_error += abs(diff)

            status = "✓" if abs(diff) < 3.0 else "✗"
            print(
                f"{block_type:>12} | {target_pct:>7.1f}% | {actual_pct:>7.1f}% | {diff:>+6.1f}% | {status}"
            )

        # Check for block types not in target
        for block_type in stats:
            if block_type not in target_distribution:
                actual_pct = stats[block_type]["percentage"]
                print(
                    f"{block_type:>12} | {'N/A':>8} | {actual_pct:>7.1f}% | {'N/A':>8} | -"
                )

        print("-" * 60)
        print(f"Total error: {total_error:.1f}%")

        return total_error

    def auto_tune(
        self, max_iterations=10, target_error=5.0, width=200, height=150, seed=42
    ):
        """
        Automatically tune terrain parameters to match target distribution

        Args:
            max_iterations: Maximum tuning iterations
            target_error: Stop when total error is below this threshold
            width, height: Map dimensions for testing
            seed: Random seed for consistency
        """
        print(
            f"Auto-tuning terrain parameters (max {max_iterations} iterations, target error: {target_error}%)"
        )
        print("=" * 70)

        for iteration in range(max_iterations):
            print(f"\nIteration {iteration + 1}/{max_iterations}")
            print("-" * 40)

            # Analyze current configuration
            result = self.analyze_distribution(width, height, seed, iterations=1)
            total_error = self.compare_to_target(result["stats"])

            if total_error <= target_error:
                print(f"\n✓ Target error achieved! Total error: {total_error:.1f}%")
                break

            # Auto-adjust thresholds
            self.config.auto_adjust_thresholds(result["stats"])

            # Validate configuration
            issues = self.config.validate_configuration()
            if issues:
                print(f"\nConfiguration issues detected:")
                for issue in issues:
                    print(f"  - {issue}")
                break

        else:
            print(f"\nReached maximum iterations. Final error: {total_error:.1f}%")

        return total_error

    def generate_report(self, output_file=None):
        """Generate a comprehensive analysis report"""
        if not self.results_history:
            print("No analysis results to report. Run analyze_distribution() first.")
            return

        latest_result = self.results_history[-1]

        report = []
        report.append("TERRAIN ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"Generated: {import_time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Analysis iterations: {len(self.results_history)}")
        report.append("")

        # Current configuration
        report.append("CURRENT CONFIGURATION")
        report.append("-" * 30)
        report.append("Base Terrain Layers:")
        for layer in self.config.base_layers:
            report.append(
                f"  {layer.name}: threshold={layer.threshold:.3f}, target={layer.target_percentage:.1f}%"
            )

        report.append("\nFeature Rules:")
        for rule in self.config.feature_rules:
            report.append(
                f"  {rule.name}: chance={rule.spawn_chance:.2f}, target={rule.target_percentage:.1f}%"
            )

        report.append("")

        # Latest statistics
        report.append("LATEST DISTRIBUTION ANALYSIS")
        report.append("-" * 35)
        stats = latest_result["stats"]
        target_dist = self.config.get_target_distribution()

        for block_type, data in sorted(
            stats.items(), key=lambda x: x[1]["percentage"], reverse=True
        ):
            actual_pct = data["percentage"]
            target_pct = target_dist.get(block_type, 0)
            diff = actual_pct - target_pct
            report.append(
                f"  {block_type}: {actual_pct:.1f}% (target: {target_pct:.1f}%, diff: {diff:+.1f}%)"
            )

        report.append("")

        # Configuration validation
        issues = self.config.validate_configuration()
        if issues:
            report.append("CONFIGURATION ISSUES")
            report.append("-" * 25)
            for issue in issues:
                report.append(f"  - {issue}")
        else:
            report.append("✓ Configuration validation passed")

        report_text = "\n".join(report)

        if output_file:
            with open(output_file, "w") as f:
                f.write(report_text)
            print(f"Report saved to: {output_file}")
        else:
            print(report_text)

    def _serialize_config(self):
        """Serialize current configuration for history tracking"""
        return {
            "base_layers": [
                (layer.name, layer.threshold, layer.target_percentage)
                for layer in self.config.base_layers
            ],
            "feature_rules": [
                (rule.name, rule.spawn_chance, rule.target_percentage)
                for rule in self.config.feature_rules
            ],
            "noise_params": self.config.noise_params.copy(),
        }


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(
        description="Advanced terrain analysis and tuning tool"
    )
    parser.add_argument("--width", type=int, default=200, help="Map width")
    parser.add_argument("--height", type=int, default=150, help="Map height")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--iterations", type=int, default=1, help="Number of analysis iterations"
    )
    parser.add_argument("--auto-tune", action="store_true", help="Auto-tune parameters")
    parser.add_argument(
        "--max-tune-iterations", type=int, default=10, help="Max auto-tune iterations"
    )
    parser.add_argument(
        "--target-error", type=float, default=5.0, help="Target error threshold"
    )
    parser.add_argument("--report", type=str, help="Generate report file")

    args = parser.parse_args()

    # Create analyzer
    analyzer = TerrainAnalyzer()

    # Validate configuration
    issues = analyzer.config.validate_configuration()
    if issues:
        print("Configuration issues detected:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nPlease fix these issues before proceeding.")
        return 1

    if args.auto_tune:
        # Auto-tune parameters
        analyzer.auto_tune(
            max_iterations=args.max_tune_iterations,
            target_error=args.target_error,
            width=args.width,
            height=args.height,
            seed=args.seed,
        )
    else:
        # Regular analysis
        result = analyzer.analyze_distribution(
            width=args.width,
            height=args.height,
            seed=args.seed,
            iterations=args.iterations,
        )

        analyzer.compare_to_target(result["stats"])

    # Generate report if requested
    if args.report:
        analyzer.generate_report(args.report)

    return 0


if __name__ == "__main__":
    import time as import_time

    sys.exit(main())
