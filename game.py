import pygame
from pathlib import Path
from enum import Enum
from bird import Bird
from game_settings import GameSettings
from pipe import Pipe


class Game:
    # Frames per second
    FPS = 30
    # Pixels between digits in score
    LETTER_SPACING = 3

    class GameState(Enum):
        menu = 0
        run = 1
        die = 2
        end = 3

    def __init__(self) -> None:
        pygame.init()

        self.load_images()

        self.screen = pygame.display.set_mode((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        pygame.display.set_icon(self.icon)

        self.clock = pygame.time.Clock()

        self.game_state = self.GameState.menu

        self.bg_pos = 0

        self.bird = Bird(Bird.BirdColor.yellow, 
                         [GameSettings.SCREEN_WIDTH // 2 - 50, GameSettings.SCREEN_HEIGHT // 2])
        
        self.pipes: list[Pipe] = []

        self.score = 0
        self.record_of_session = 0

        # Create txt file for record saving if not exists
        data_file_path = Path.joinpath(Path.cwd(), "data.txt")
        if not Path.is_file(data_file_path):
            f = open(data_file_path, "w")
            f.write("0")
            f.close()
        
        with open("data.txt", "r") as f:
            line = f.readline()
            self.record_of_session = int(line)

        # Is holding space
        self._space_hold = False
        # Time of last pipe creation
        self._last_pipe_create_time = pygame.time.get_ticks()
        # Index of next pipe
        self._next_pipe = 0
    
    def update(self) -> None:
        delta_time = self.clock.get_time() / 1000.0

        # Change background position
        self.bg_pos -= delta_time * GameSettings.game_speed
        if self.bg_pos <= -GameSettings.SCREEN_WIDTH:
            self.bg_pos = 0
        
        # Handle key presses
        keys = pygame.key.get_pressed()

        if self.game_state == self.GameState.die:
            self.bird.update(delta_time)
            if keys[pygame.K_SPACE]:
                self.restart()

        if keys[pygame.K_SPACE] and self._space_hold == False and self.game_state == self.GameState.menu:
            # Start game if space pressed in menu
            self.start_game()
        if keys[pygame.K_SPACE] and self._space_hold == False and self.game_state == self.GameState.run:
            self._space_hold = True
            self.bird.flap()
        elif not keys[pygame.K_SPACE] and self.game_state not in {self.GameState.end, self.GameState.die}:
            self._space_hold = False
        
        if self.game_state == self.GameState.run:
            # Handle bird update
            falled = self.bird.update(delta_time)
            if falled:
                self.losed()

            # Pipe handler
            if pygame.time.get_ticks() - self._last_pipe_create_time >= Pipe.DIST_BETWEEN:
                self._last_pipe_create_time = pygame.time.get_ticks()
                self.add_pipe()
                self.check_and_remove_pipe()

            # Check if passed the center of next pipe, and add score
            self.check_score()

            # Check collision with pipes
            if self.check_collision():
                self.losed()

            for pipe in self.pipes:
                pipe.update(delta_time)
    
    def draw(self) -> None:
        """
        Draw everything on screen
        """
        # Draw background
        self.screen.blit(self.image_bg_day, (self.bg_pos, 0))
        self.screen.blit(self.image_bg_day, (self.bg_pos + GameSettings.SCREEN_WIDTH, 0))

        match self.game_state:
            case self.GameState.run | self.GameState.die:
                # Draw bird
                self.bird.draw(self.screen)

                # Draw pipes
                for pipe in self.pipes:
                    pipe.draw(self.screen)
                
                # Draw score
                num = self.number_surface(self.score)
                self.screen.blit(num, (0, 5))

            case self.GameState.menu:
                # Draw menu
                menu_rect = self.image_menu.get_rect()
                menu_rect.center = self.screen.get_rect().center
                self.screen.blit(self.image_menu, menu_rect)

                num = self.number_surface(self.record_of_session)
                num_rect = num.get_rect()
                num_rect.centerx = self.screen.get_rect().centerx
                num_rect.centery = 50
                self.screen.blit(num, num_rect)
            
            case self.GameState.die:
                end_rect = self.image_end.get_rect()
                end_rect.center = self.screen.get_rect().center
                end_rect.centery -= 20
                self.screen.blit(self.image_end, end_rect)
    
    def number_surface(self, num: int = 0) -> pygame.Surface:
        """
        Returns a surface containing image of given number
        """
        str_score = str(num)
        pos = 5
        digit_width = self.image_digits[0].get_width()
        digit_height = self.image_digits[0].get_height()
        digit_difference = digit_width - self.image_digits[1].get_width()

        drawing_list: tuple[pygame.Surface, tuple[int, int]] = []

        for dig in str_score:
            drawing_list.append((self.image_digits[int(dig)], (pos, 0)))
            if dig == "1":
                pos -= digit_difference
            pos += digit_width + self.LETTER_SPACING

        result = pygame.Surface((pos, digit_height), pygame.SRCALPHA, 32)
        result = result.convert_alpha()
        
        for img, pos in drawing_list:
            result.blit(img, pos)
        
        return result

    def load_images(self) -> None:
        # Load images from sprites folder
        from pygame.image import load
        
        sprites_path = GameSettings.SPRITES_PATH

        self.icon = load(Path.joinpath(sprites_path.parent, "favicon.ico"))

        self.image_menu = pygame.transform.scale_by(
            load(Path.joinpath(sprites_path, "message.png")),
            1.25)
    
        self.image_end = load(Path.joinpath(sprites_path, "gameover.png"))

        self.image_bg_day = load(Path.joinpath(sprites_path, "background-day.png"))
        self.image_bg_night = load(Path.joinpath(sprites_path, "background-night.png"))

        self.image_digits = [load(Path.joinpath(sprites_path, f"{i}.png"))
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
        ind = self._next_pipe - 1
        if ind > 0:
            prev_pipe = self.pipes[self._next_pipe - 1]
        else:
            prev_pipe = Pipe(pos = -200)
        f, s = pipe.rect_bottom, pipe.rect_top
        pf, ps = prev_pipe.rect_bottom, prev_pipe.rect_top
        return self.bird.rect.colliderect(f) or self.bird.rect.colliderect(s) or \
            self.bird.rect.colliderect(pf) or self.bird.rect.colliderect(ps)
    
    def get_next_pipe(self) -> Pipe:
        return self.pipes[self._next_pipe]
    
    def start_game(self) -> None:
        self.game_state = self.GameState.run
        self.add_pipe()
    
    def losed(self) -> None:
        GameSettings.game_speed = 0
        self.game_state = self.GameState.die
        self.record_of_session = max(self.record_of_session, self.score)
    
    def restart(self) -> None:
        GameSettings.game_speed = 50

        self.clock = pygame.time.Clock()

        self.game_state = self.GameState.menu

        self.bg_pos = 0

        self.bird = Bird(Bird.BirdColor.yellow, 
                         [GameSettings.SCREEN_WIDTH // 2 - 50, GameSettings.SCREEN_HEIGHT // 2])
        
        self.pipes: list[Pipe] = []

        self.score = 0

        self._space_hold = True
        self._last_pipe_create_time = pygame.time.get_ticks()
        self._next_pipe = 0
    
    def end(self) -> None:
        with open("data.txt", "w") as f:
            f.write(str(self.record_of_session))

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
        self.main_loop()
        self.end()
        pygame.quit()