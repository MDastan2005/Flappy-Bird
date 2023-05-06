from pathlib import Path

class GameSettings:
    """
    Game constants and variables
    """

    SCREEN_WIDTH = 288
    SCREEN_HEIGHT = 512
    
    GRAVITY = 1000
    game_speed = 50
    BIRD_FLAP_FORCE = 250

    SPRITES_PATH = Path("assets/sprites")
    AUDIO_PATH = Path("assets/audio")
    