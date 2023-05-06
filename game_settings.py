from pathlib import Path

class GameSettings:
    SCREEN_WIDTH = 288
    SCREEN_HEIGHT = 512
    
    gravity = 50
    game_speed = 50
    bird_flop_force = 300

    sprites_path = Path("assets/sprites")
    