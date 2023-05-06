import pygame
from pathlib import Path
from enum import Enum
from bird import Bird
from game_settings import GameSettings
from pipe import Pipe


class Game:
    FPS = 30
    LETTER_SPACING = 3

    class GameState(Enum):
        menu = 0
        run = 1
        die = 2
        end = 3

    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")

        self.clock = pygame.time.Clock()

        self.game_state = self.GameState.menu

        self.bg_pos = 0

        self.bird = Bird(Bird.BirdColor.yellow, 
                         [GameSettings.SCREEN_WIDTH // 2 - 50, GameSettings.SCREEN_HEIGHT // 2])
        
        self.pipes: list[Pipe] = []

        self.score = 0

        self._space_hold = False
        self._last_pipe_create_time = pygame.time.get_ticks()
        self._next_pipe = 0
    
    def update(self) -> None:
        delta_time = self.clock.get_time() / 1000.0
        self.bg_pos -= delta_time * GameSettings.game_speed
        if self.bg_pos <= -GameSettings.SCREEN_WIDTH:
            self.bg_pos = 0
        
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.game_state != self.GameState.run:
            self.start_game()
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            self.bird.flop()
        else:
            self._space_hold = False
        
        if self.game_state == self.GameState.run:
            falled = self.bird.update(delta_time)
            # TODO: handle falled event

            if pygame.time.get_ticks() - self._last_pipe_create_time >= Pipe.DIST_BETWEEN:
                self._last_pipe_create_time = pygame.time.get_ticks()
                self.add_pipe()
                self.check_and_remove_pipe()

            self.check_score()

            if self.check_collision():
                GameSettings.game_speed = 0

            for pipe in self.pipes:
                pipe.update(delta_time)
    
    def draw(self) -> None:
        # Draw background
        self.screen.blit(self.image_bg_day, (self.bg_pos, 0))
        self.screen.blit(self.image_bg_day, (self.bg_pos + GameSettings.SCREEN_WIDTH, 0))

        # Draw bird
        self.bird.draw(self.screen)

        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)
        
        # Draw score
        str_score = str(self.score)
        pos = 5
        digit_width = self.image_digits[0].get_width()
        digit_difference = digit_width - self.image_digits[1].get_width()
        for dig in str_score:
            self.screen.blit(self.image_digits[int(dig)], (pos, 5))
            if dig == "1":
                pos -= digit_difference
            pos += digit_width + self.LETTER_SPACING

    def load_images(self) -> None:
        sprites_path = GameSettings.sprites_path
        self.image_bg_day = pygame.image.load(Path.joinpath(sprites_path, "background-day.png"))
        self.image_bg_night = pygame.image.load(Path.joinpath(sprites_path, "background-night.png"))

        self.image_digits = [pygame.image.load(Path.joinpath(sprites_path, f"{i}.png"))
                             for i in range(10)]
    
    def add_pipe(self) -> None:
        if len(self.pipes) == 0:
            pipe = Pipe(diff=Pipe.Gaps.easy, pos=GameSettings.SCREEN_WIDTH + 10 + Pipe.DIST_BETWEEN)
            self.pipes.append(pipe)
        if len(self.pipes) > 0:
            pipe = Pipe(diff=Pipe.Gaps.easy, pos=self.pipes[-1].rect_top.right + Pipe.DIST_BETWEEN)
            self.pipes.append(pipe)
    
    def check_and_remove_pipe(self) -> None:
        if len(self.pipes) != 0:
            if self.pipes[0].pos <= -100:
                self.pipes.pop(0)
                self._next_pipe -= 1
    
    def check_score(self) -> None:
        if self.bird.get_center() >= self.get_next_pipe().get_center():
            self._next_pipe += 1
            self.score += 1

    def check_collision(self) -> bool:
        pipe = self.get_next_pipe()
        f, s = pipe.rect_bottom, pipe.rect_top
        return self.bird.rect.colliderect(f) or self.bird.rect.colliderect(s)
    
    def get_next_pipe(self) -> Pipe:
        return self.pipes[self._next_pipe]
    
    def start_game(self) -> None:
        self._space_hold = True
        self.game_state = self.GameState.run
        self.add_pipe()

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