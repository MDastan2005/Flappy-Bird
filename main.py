import pygame
from pathlib import Path
from enum import IntEnum, Enum
import random


class GameSettings:
    gravity = 70
    game_speed = 50
    bird_flop_force = 400


class Pipe:
    GAPS = (100, 70, 50)
    OFFSET = 10
    TIME_BETWEEN = 3000

    class Gaps(IntEnum):
        easy = 0
        medium = 1
        hard = 2
    
    def __init__(self, diff = Gaps.easy, pos: list[int] = 0) -> None:
        self.diff = diff
        self.pos = [pos, self.get_random_y()]
    
    def draw(self, screen: pygame.Surface) -> None:
        regular, flipped = self.get_image()
        x, y = self.pos
        screen.blit(flipped, (x, y - flipped.get_height()))
        screen.blit(regular, (x, y + self.gap))
    
    def update(self, delta_time: float) -> None:
        self.pos[0] -= delta_time * GameSettings.game_speed * 2
    
    def get_random_y(self) -> int:
        return random.randint(self.OFFSET, Game.SCREEN_HEIGHT - self.gap - self.OFFSET)
    
    def get_image(self) -> tuple[pygame.Surface, pygame.Surface]:
        return self.image_pipes[self.diff]
    
    @property
    def gap(self) -> int:
        return self.GAPS[self.diff]

    @classmethod
    def load_images(self, sprites_path) -> None:
        pipe_colors = ("green", "red")
        self.image_pipes = []
        for color in pipe_colors:
            image = pygame.image.load(Path.joinpath(sprites_path, f"pipe-{color}.png"))
            self.image_pipes.append((image, pygame.transform.flip(image, flip_x=False, flip_y=True)))


class Bird:
    ANIMATION_FRAMES = 3
    HEIGHT = 24

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
        self.pos = pos
        self.velocity = 0
    
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image_birds[self.color][self.state], self.pos)
    
    def update(self, delta_time: float) -> bool:
        self.pos[1] += self.velocity * delta_time

        if self.falled():
            self.pos[1] = Game.SCREEN_HEIGHT - self.HEIGHT
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
        return self.pos[1] + self.HEIGHT > Game.SCREEN_HEIGHT
    
    @classmethod
    def load_images(self, sprites_path) -> None:
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


class Game:
    SCREEN_WIDTH = 288
    SCREEN_HEIGHT = 512
    FPS = 30
    ASSETS_PATH = Path("assets")

    class GameState(Enum):
        menu = 0
        run = 1
        die = 2
        end = 3

    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")

        self.clock = pygame.time.Clock()

        self.game_state = self.GameState.menu

        self.bg_pos = 0

        self.bird = Bird(Bird.BirdColor.yellow, 
                         [self.SCREEN_WIDTH // 2 - 50, self.SCREEN_HEIGHT // 2])
        
        self.pipes: list[Pipe] = []

        self._space_hold = False
        self._last_pipe_create_time = pygame.time.get_ticks()
    
    def update(self) -> None:
        delta_time = self.clock.get_time() / 1000.0
        self.bg_pos -= delta_time * GameSettings.game_speed
        if self.bg_pos <= -self.SCREEN_WIDTH:
            self.bg_pos = 0
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            self._space_hold = True
            self.game_state = self.GameState.run
            self.bird.flop()
        else:
            self._space_hold = False
        
        if self.game_state == self.GameState.run:
            falled = self.bird.update(delta_time)
            # TODO: handle falled event

            if pygame.time.get_ticks() - self._last_pipe_create_time >= Pipe.TIME_BETWEEN:
                self._last_pipe_create_time = pygame.time.get_ticks()
                self.add_pipe()
                self.check_and_remove_pipe()

            for pipe in self.pipes:
                pipe.update(delta_time)
    
    def draw(self) -> None:
        self.screen.blit(self.image_bg_day, (self.bg_pos, 0))
        self.screen.blit(self.image_bg_day, (self.bg_pos + self.SCREEN_WIDTH, 0))
        self.bird.draw(self.screen)

        for pipe in self.pipes:
            pipe.draw(self.screen)

    def load_images(self) -> None:
        sprites_path = Path.joinpath(self.ASSETS_PATH, "sprites/")
        self.image_bg_day = pygame.image.load(Path.joinpath(sprites_path, "background-day.png"))
        self.image_bg_night = pygame.image.load(Path.joinpath(sprites_path, "background-night.png"))

        self.image_digits = [pygame.image.load(Path.joinpath(sprites_path, f"{i}.png"))
                             for i in range(10)]
        
        Bird.load_images(sprites_path)
        Pipe.load_images(sprites_path)
    
    def add_pipe(self) -> None:
        pipe = Pipe(diff=Pipe.Gaps.medium, pos=self.SCREEN_WIDTH)
        self.pipes.append(pipe)
    
    def check_and_remove_pipe(self) -> None:
        if len(self.pipes) != 0:
            if self.pipes[0].pos[0] <= -100:
                self.pipes.pop(0)

    def main_loop(self) -> None:
        while self.game_state != self.GameState.end:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_state = self.GameState.end
                    return
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(self.FPS)
    
    def run(self) -> None:
        self.load_images()
        self.main_loop()
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
