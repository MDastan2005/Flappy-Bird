import pygame
from pathlib import Path
from enum import IntEnum
from game_settings import GameSettings


class Bird:
    # Number of frames each animation state stay.
    ANIMATION_FRAMES = 3

    class BirdState(IntEnum):
        """
        Animation states for wings flapping
        """
        down = 0
        mid = 1
        up = 2


    class BirdColor(IntEnum):
        """
        Bird's image color
        """
        red = 0
        blue = 1
        yellow = 2

    def __init__(self, color = BirdColor.yellow, pos: list[int] = [0, 0]) -> None:
        """_summary_

        Params:
            color: color.
            velocity: the velocity by Y axis
            state: animation state.
            _anim_counter: number of frames for current animation state.
            tilt: angle to rotate when drawing on screen. Calculated from velocity.
            rect: contains information of image size and position.
        """
        self.color = color
        self.velocity = 0
        self.state = self.BirdState.mid
        self._anim_counter = 0
        self.tilt = 0
        self.load_images()
        x, y = pos
        self.rect = pygame.Rect(x, y, *self.get_image().get_size())
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Rotates the image by the tilt and draws into the screen.
        """
        img = pygame.transform.rotate(self.get_image(), -self.tilt)
        screen.blit(img, self.rect)
    
    def update(self, delta_time: float) -> bool:
        """
        Event handler. Checks for collision with floor, calculates position, velocity, tilt.
        Handles animation.

        Args:
            delta_time (float): gets from main loop.

        Returns:
            bool: if bird collided with floor.
        """
        # Calculate position and check for collision with floor
        self.rect.top += self.velocity * delta_time

        if self.falled():
            self.rect.top = GameSettings.SCREEN_HEIGHT - self.rect.height
            return True

        # Calculate velocity
        self.velocity += GameSettings.GRAVITY * delta_time

        # Calculate tilt from velocity
        val_max = 400.0
        val_min = -100.0
        val_for_tilt = max(val_min, min(val_max, float(self.velocity)))
        val_range = (val_max - val_min)
        tilt_max = 60.0
        tilt_min = -30.0
        tilt_range = (tilt_max - tilt_min)
        self.tilt = (((val_for_tilt - val_min) * tilt_range) / val_range) + tilt_min

        # Handle animation
        if self.state != self.BirdState.up:
            self._anim_counter += 1
            if self._anim_counter == self.ANIMATION_FRAMES:
                self.state += 1
                self._anim_counter = 0
        return False

    def flap(self) -> None:
        """
        Changes velocity and restarts animation.
        """
        self.velocity = -GameSettings.BIRD_FLAP_FORCE
        self.state = self.BirdState.down
        self._anim_counter = 0
    
    def falled(self) -> bool:
        """
        Checks if collided with floor
        """
        return self.rect.top + self.rect.height > GameSettings.SCREEN_HEIGHT

    def get_image(self) -> pygame.Surface:
        """
        Returns image of correct color and animation state
        """
        return self.image_birds[self.color][self.state]

    def get_center(self) -> int:
        """
        Returns center of the rect by X axis
        """
        return self.rect.centerx
    
    @classmethod
    def load_images(self) -> None:
        """
        Loads all images from sprites folder
        """
        sprites_path = GameSettings.SPRITES_PATH
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