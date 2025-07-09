# Claude Code Context

This project uses a comprehensive test suite. **ALWAYS run `python -m pytest` after making code changes and fix any failures before completing tasks.**

For full project context, see AGENTS.md.

## Key Testing Rules
- Never commit/finish work with failing tests
- Use focused testing during development but always verify with full suite
- Test suite is fast and comprehensive - leverage it heavily

## Quick Project Overview
- 2D tile-based survival game (Python + Pygame)
- Top-down perspective with strict 2D grid positions
- Source code in `src/`, tests in `tests/`, utilities in `scripts/`

## Key Files
- `src/game.py` - Core game logic
- `src/player.py` - Player movement, controls, mining
- `src/terrain_generator_v2.py` - Procedural terrain (Perlin noise)
- `src/lighting.py` - Day/night cycle and lighting effects
- `src/camera.py` - Camera movement and viewport
- `src/block.py` - Block types and properties
- `src/main.py` - Main game loop and entry point

## Coding Guidelines
- Prioritize clarity and readability
- Avoid new external dependencies unless requested
- Use functional decomposition for large functions
- Include docstrings explaining assumptions
- Use `pygame_setup` fixture for new tests (don't call pygame.init())