import pygame
from pathlib import Path
from enum import IntEnum
from game_settings import GameSettings


class Bird:
    ANIMATION_FRAMES = 3

    class BirdState(IntEnum):
        down = 0
        mid = 1
        up = 2


    class BirdColor(IntEnum):
        red = 0
        blue = 1
        yellow = 2

    def __init__(self, color = BirdColor.yellow, pos: list[int] = [0, 0]) -> None:
        self.state = self.BirdState.mid
        self._anim_counter = 0
        self.color = color
        self.velocity = 0
        self.load_images()
        x, y = pos
        self.rect = pygame.Rect(x, y, *self.get_image().get_size())
    
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.get_image(), self.rect)
    
    def update(self, delta_time: float) -> bool:
        self.rect.top += self.velocity * delta_time

        if self.falled():
            self.rect.top = GameSettings.SCREEN_HEIGHT - self.rect.height
            return True

        self.velocity += GameSettings.gravity

        if self.state != self.BirdState.up:
            self._anim_counter += 1
            if self._anim_counter == self.ANIMATION_FRAMES:
                self.state += 1
                self._anim_counter = 0
        return False

    def flop(self) -> None:
        self.velocity = -GameSettings.bird_flop_force
        self.state = self.BirdState.down
        self._anim_counter = 0
    
    def falled(self) -> bool:
        return self.rect.top + self.rect.height > GameSettings.SCREEN_HEIGHT

    def get_image(self) -> pygame.Surface:
        return self.image_birds[self.color][self.state]

    def get_center(self) -> int:
        return self.rect.centerx
    
    @classmethod
    def load_images(self) -> None:
        sprites_path = GameSettings.sprites_path
        birds_colors = ("redbird", "bluebird", "yellowbird")
        self.image_birds = []
        for color in birds_colors:
            states = ("downflap", "midflap", "upflap")
            temp_list = []
            for state in states:
                temp_list.append(
                    pygame.image.load(Path.joinpath(sprites_path, f"{color}-{state}.png"))
                )
            self.image_birds.append(temp_list)