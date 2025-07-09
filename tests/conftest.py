import pytest
import pygame
import os


@pytest.fixture(scope="session")
def pygame_setup():
    os.environ["SDL_VIDEODRIVER"] = "dummy"

    # need display.set_mode for pygame.image.load.convert_alpha
    # functions called at sprite loading time to work
    pygame.display.set_mode((1, 1))
    pygame.init()
    yield
    pygame.quit()
