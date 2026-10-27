import arcade

# GAME CONSTANTS
WIDTH = 800
HEIGHT = 600
TILE_SIZE = 32
PLAYER_SIZE = 24
TITLE = "Little Yellow"

class Game(arcade.Window):
    """Main App Class"""
    
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, TITLE)
        self.background_color = arcade.csscolor.BLACK

        self.player_list = None
        self.floor_list = None
        self.player = None

    def setup(self):

        self.player_list = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()

        self.player = arcade.SpriteSolidColor(
            PLAYER_SIZE, PLAYER_SIZE, color=arcade.color.ORANGE
        )

        self.player.center_x = WIDTH / 2
        self.player.center_y = TILE_SIZE + (PLAYER_SIZE / 2)
        self.player_list.append(self.player)

        # assumes WIDTH=800 and TILE_SIZE=32
        for i in range(25):
            floor = arcade.SpriteSolidColor(TILE_SIZE, TILE_SIZE, color=arcade.csscolor.YELLOW)
            floor.center_x = i * TILE_SIZE + TILE_SIZE / 2
            floor.center_y = 16
            self.floor_list.append(floor)
            
    def on_draw(self):
        self.clear()
        self.player_list.draw()
        self.floor_list.draw()


def main():
    window = Game()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()