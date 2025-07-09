import pygame
from game import Game


def main():
    """Main entry point - create and run the game"""
    # Initialize PyGame
    pygame.init()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
