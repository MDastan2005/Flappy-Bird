import pygame
from pathlib import Path


class Game:
    SCREEN_WIDTH = 288
    SCREEN_HEIGHT = 512
    FPS = 30
    ASSETS_PATH = Path("assets")
    SPEED = 50

    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")

        self.clock = pygame.time.Clock()

        self.bg_pos = 0
    
    def update(self) -> None:
        delta_time = self.clock.get_time() / 1000.0
        self.bg_pos -= delta_time * self.SPEED
        if self.bg_pos <= -self.SCREEN_WIDTH:
            self.bg_pos = 0
    
    def draw(self) -> None:
        self.screen.blit(self.image_bg_day, (self.bg_pos, 0))
        self.screen.blit(self.image_bg_day, (self.bg_pos + self.SCREEN_WIDTH, 0))

    def load_images(self) -> None:
        sprites_path = Path.joinpath(self.ASSETS_PATH, "sprites/")
        self.image_bg_day = pygame.image.load(Path.joinpath(sprites_path, "background-day.png"))
        self.image_bg_night = pygame.image.load(Path.joinpath(sprites_path, "background-night.png"))

        self.image_digits = [pygame.image.load(Path.joinpath(sprites_path, f"{i}.png"))
                             for i in range(10)]
        
        birds_colors = {"redbird", "bluebird", "yellowbird"}
        self.image_birds = []
        for color in birds_colors:
            states = {"downflap", "midflap", "upflap"}
            for state in states:
                self.image_birds.append(
                    pygame.image.load(Path.joinpath(sprites_path, f"{color}-{state}.png"))
                )

    def main_loop(self) -> None:
        self.run = True
        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
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

# Прочитал и начал задание ночью. Решил быстро сделать началные фишки. Извените что мало добавил мало фишек в комит.