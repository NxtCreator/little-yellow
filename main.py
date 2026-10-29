import arcade

# GAME CONSTANTS
WIDTH = 800
HEIGHT = 600
GRAVITY = 1
PLAYER_JUMP_SPEED = 15
TILE_SIZE = 32
PLAYER_SIZE = 24
PLAYER_SPEED = 5
TITLE = "Little Yellow"

class Game(arcade.Window):
    """Main app class: manages the game window and its contents"""
    
    def __init__(self):
        # initialize the Arcade game window using our constants
        super().__init__(WIDTH, HEIGHT, TITLE)
        self.background_color = arcade.csscolor.BLACK

        self.physics_engine = None

        # Initialize these attributes so setup() can assign the
        # SpriteLists and player sprite before the game is drawn
        self.player_list = None
        self.floor_list = None
        self.player = None
        self.hidden_list = None
        
        # Remember which keys are being held
        self.left_pressed = False
        self.right_pressed = False

    def setup(self):
        # create SpriteLists to organize the player and floor sprites.
        self.player_list = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()
        self.hidden_list = arcade.SpriteList()

        floor_center_y = TILE_SIZE / 2


        self.player = arcade.SpriteSolidColor(
            PLAYER_SIZE, PLAYER_SIZE, color=arcade.csscolor.ORANGE_RED
        )

        
        # Center the player horizontally and place its bottom edge
        # on the floor's top edge
        self.player.center_x = WIDTH / 2
        self.player.center_y = floor_center_y + TILE_SIZE / 2 + PLAYER_SIZE / 2
        
        # Store the player so the SpriteList can draw it
        self.player_list.append(self.player)

        # Create enough tiles to span the window's width.
        # This currently assumes WIDTH is divisible  by TILE_SIZE
        for i in range(25):
            floor = arcade.SpriteSolidColor(TILE_SIZE, TILE_SIZE, color=arcade.csscolor.YELLOW)

            # Calculate each tile's center from is left edge,
            # so the tiles sit side by side without gaps
            floor.center_x = i * TILE_SIZE + TILE_SIZE / 2
            floor.center_y = floor_center_y

            # store each tile in the list so we can draw the floor
            self.floor_list.append(floor)

        floor_top = floor_center_y + TILE_SIZE / 2

        hidden_tile = arcade.SpriteSolidColor(TILE_SIZE, TILE_SIZE,
                                              color=arcade.csscolor.YELLOW)
        hidden_tile.center_x = WIDTH / 2 + 3 * TILE_SIZE
        hidden_tile.center_y = floor_top + 2 * TILE_SIZE + TILE_SIZE / 2
        self.hidden_list.append(hidden_tile)
        
        # create a physics engine to handle collisions and gravity
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            walls = self.floor_list,
            gravity_constant=GRAVITY
        )
        
        self.physics_engine.enable_multi_jump(2)
            
    def on_draw(self):
        # Clear the previous frame before drawing the current scene.
        self.clear()

        # Draw the floor first so the player appears in front of it.
        self.floor_list.draw()
        self.player_list.draw()

    def on_update(self, delta_time):
        if self.left_pressed:
            self.player.change_x = -PLAYER_SPEED
        elif self.right_pressed:
            self.player.change_x  = PLAYER_SPEED
        else:
            self.player.change_x = 0
        self.physics_engine.update()

        colliding_hidden = arcade.check_for_collision_with_list(self.player, self.hidden_list)

        # Make visible all the hidden tiles a player touches
        for hidden_tile in colliding_hidden:
            self.hidden_list.remove(hidden_tile)
            self.floor_list.append(hidden_tile)



    def on_key_press(self, key, modifiers):
        
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.physics_engine.jump(PLAYER_JUMP_SPEED)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False


def main():
    window = Game()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()