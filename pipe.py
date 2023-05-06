import pygame
from pathlib import Path
from enum import IntEnum
import random
from game_settings import GameSettings


class Pipe:
    GAPS = (150, 100, 70)
    OFFSET = 10
    DIST_BETWEEN = 120

    class Gaps(IntEnum):
        easy = 0
        medium = 1
        hard = 2
    
    def __init__(self, diff = Gaps.easy, pos: list[int] = 0) -> None:
        self.diff = diff
        x, y = pos, self.get_random_y()
        self.load_images()
        regular, flipped = self.get_image()
        self.rect_top = pygame.Rect(x, y - flipped.get_height(), *flipped.get_size())
        self.rect_bottom = pygame.Rect(x, y + self.gap, *regular.get_size())
    
    def draw(self, screen: pygame.Surface) -> None:
        regular, flipped = self.get_image()
        screen.blit(regular, self.rect_bottom)
        screen.blit(flipped, self.rect_top)
    
    def update(self, delta_time: float) -> None:
        self.rect_bottom.left -= delta_time * GameSettings.game_speed * 2
        self.rect_top.left -= delta_time * GameSettings.game_speed * 2
    
    def get_random_y(self) -> int:
        return random.randint(self.OFFSET, GameSettings.SCREEN_HEIGHT - self.gap - self.OFFSET)
    
    def get_image(self) -> tuple[pygame.Surface, pygame.Surface]:
        return self.image_pipes[self.diff]
    
    def get_center(self) -> int:
        return self.rect_top.centerx

    @property
    def gap(self) -> int:
        return self.GAPS[self.diff]

    @property
    def pos(self) -> int:
        return self.rect_top.left

    @classmethod
    def load_images(self) -> None:
        sprites_path = GameSettings.sprites_path
        pipe_colors = ("green", "red")
        self.image_pipes = []
        for color in pipe_colors:
            image = pygame.image.load(Path.joinpath(sprites_path, f"pipe-{color}.png"))
            self.image_pipes.append((image, pygame.transform.flip(image, flip_x=False, flip_y=True)))