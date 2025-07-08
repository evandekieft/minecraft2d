import pytest
import pygame
import os


@pytest.fixture(scope="session")
def pygame_setup():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    yield
    pygame.quit()
