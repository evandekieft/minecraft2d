# 📄 agents.md — AI Coding Assistant Context Guide for This Project

This file provides **technical context and coding guidelines** to improve AI coding assistant performance on this project.

For general project info, installation, and gameplay overview, refer to **README.md**.

---

## 🕹️ Project Summary
- **Game Type:** 2D Overhead Tile-Based Survival Game (Inspired by Minecraft)
- **Engine/Framework:** Python + Pygame
- **Perspective:** Top-down (Zelda-like) with strict 2D grid positions
- **Key Features:** Procedural world generation, day/night cycle, resource gathering.

---

## Top level directory structure

- src: Game source code
- tests: All tests (pytest)
- scripts: Helpers and utilities for development, not invoked in running game

## 🗺️ Key Modules & Systems

Here’s where major game systems live in the codebase:

- src/main.py:        Main entry point; initializes and runs Game object
- src/game.py:        Top level pygame while loop, event handling. 
- src/game_world.py:  Core gameplay logic with primary draw and update functions.
- src/block.py:       Block types, properties, and rendering logic
- src/constants.py:   Game-wide constants and configuration values
- src/camera.py:      Camera movement and viewport management	
- src/lighting.py:    Lighting effects and day/night cycle
- src/menu.py:        Game menus and UI navigation
- src/player.py:	   Player movement, controls, and animation
- src/sprites.py:	   Sprite loading and management
- src/terrain_generator.py:	Procedural terrain generation (Perlin noise based)
- src/terrain_config.py:	Configuration and parameters for terrain_generator.py
- src/world_manager.py:	World state management and chunk loading

> ✅ Refer to the actual source code for implementation details.

---

## 🧪 Testing & Debugging Notes

Use `pytest` for testing. Tests are located under `tests/` and named `test_*.py`. 
You're expected to run pytest from the root project directory.

The test suite is comprehensive and fast. The full suite should be run before declaring work finished.

Each file typically tests the module of the same name (e.g., test_player.py tests player.py).
Tests use pytest conventions. New test files can be added without needing to update this guide; just follow the naming pattern.

Avoid calling pygame.init() in newly created tests. Instead, prefer use of the fixture `pygame_setup` in `tests/conftest.py`, which can call this for you.

### Testing Requirements for AI Assistants
- **ALWAYS run the full test suite** (`pytest -v`) after making any code changes
- If tests fail, fix them before considering the task complete
- Never commit or finish work with failing tests
- Use specific test commands for focused testing during development, but always end with full suite verification

---

## 🤖 Tips for AI Coding Assistants
When generating code for this project:
- Prioritize clarity and readability.
- Avoid introducing new external dependencies unless explicitly requested.
- Use functional decomposition: split large functions into smaller helpers.
- Include docstrings and inline comments explaining assumptions.

---

## Intended Future Tasks (Not implemented yet)
- Crafting system that can combine blocks to turn into other ones
- Enemies that spawn
- Tools (e.g. pickaxe) that speed up mining or can fight enemies
- Player health

---

## 🔗 References
For project basics, see:
- `README.md`
- Docstrings in `src/` modules.

---

> ✅ **This file may evolve as the project grows. Update it regularly to maximize coding assistant effectiveness.**
