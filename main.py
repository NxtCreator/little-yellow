import arcade

# ---------------------------------------------------------------------------
# GAME CONSTANTS
# ---------------------------------------------------------------------------

# Window
WIDTH = 800
HEIGHT = 600
TITLE = "Little Yellow"

# Sizes (the player is smaller than a platform square on purpose)
TILE_SIZE = 32
PLAYER_SIZE = 24

# Movement and physics
GRAVITY = 1
PLAYER_SPEED = 4
PLAYER_JUMP_SPEED = 15
MAX_JUMPS = 2          # 2 = one jump plus one extra jump in mid-air
FALL_LIMIT = -200      # below this y, the player has fallen out of the world


class Game(arcade.Window):
    """Main game class: owns the window, the level, and the game loop."""

    # -----------------------------------------------------------------------
    # Setup
    # -----------------------------------------------------------------------

    def __init__(self):
        super().__init__(WIDTH, HEIGHT, TITLE)
        self.background_color = arcade.csscolor.BLACK

        # Sprites and lists. Declared here, built in setup().
        self.player = None
        self.player_list = None
        self.floor_list = None      # solid tiles, also the engine's "walls"
        self.hidden_list = None     # not drawn and not solid until touched
        self.goal_list = None

        # The player's two faces (left and right)
        self.left_texture = None
        self.right_texture = None

        self.physics_engine = None

        # Level state
        self.spawn_point = None
        self.won = False

        # Keys currently held. on_update turns these into movement.
        self.left_pressed = False
        self.right_pressed = False

    def setup(self):
        """Build the level. Call it again to restart."""
        self.won = False

        # Brand-new lists every time, so a restart never piles
        # new tiles on top of the old ones.
        self.player_list = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()
        self.hidden_list = arcade.SpriteList()
        self.goal_list = arcade.SpriteList()

        self.left_texture = arcade.load_texture("assets/little_yellow_left.png")
        self.right_texture = arcade.load_texture("assets/little_yellow_right.png")

        # --- Floor ---
        # Everything vertical below is measured from these two numbers.
        floor_center_y = TILE_SIZE / 2
        floor_top = floor_center_y + TILE_SIZE / 2

        # Assumes WIDTH = 800 and TILE_SIZE = 32 (25 tiles fill the window).
        for i in range(25):
            floor = arcade.Sprite("assets/floor.png")

            # Sprites are positioned by their center, so shift each tile
            # half a tile to the right of its left edge.
            floor.center_x = i * TILE_SIZE + TILE_SIZE / 2
            floor.center_y = floor_center_y
            self.floor_list.append(floor)

        # --- Player ---
        self.player = arcade.Sprite(self.right_texture)
        self.player.center_x = WIDTH / 2
        # Bottom edge of the player rests on the floor's top edge.
        self.player.center_y = floor_top + PLAYER_SIZE / 2
        self.player_list.append(self.player)

        # Where to come back to after falling out of the world.
        self.spawn_point = self.player.position

        # --- Hidden tile (test) ---
        # Lives in its own list so the physics engine ignores it
        # until the player reveals it.
        hidden_tile = arcade.Sprite("assets/floor.png")
        hidden_tile.center_x = WIDTH / 2 + 3 * TILE_SIZE
        hidden_tile.center_y = floor_top + TILE_SIZE / 2
        self.hidden_list.append(hidden_tile)

        # --- Goal (test) ---
        goal = arcade.SpriteSolidColor(TILE_SIZE, TILE_SIZE, color=arcade.csscolor.GOLD)
        goal.center_x = WIDTH / 2 + 5 * TILE_SIZE
        goal.center_y = floor_top + 5 * TILE_SIZE + TILE_SIZE / 2
        self.goal_list.append(goal)

        # --- Physics ---
        # Created last, because it needs the player and the floor to exist.
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            walls=self.floor_list,
            gravity_constant=GRAVITY,
        )
        self.physics_engine.enable_multi_jump(MAX_JUMPS)

    # -----------------------------------------------------------------------
    # Game loop
    # -----------------------------------------------------------------------

    def on_update(self, delta_time):
        """Runs every frame: input -> physics -> reveals -> respawn -> win."""
        # Freeze the game once the level is won.
        if self.won:
            return

        # 1. Held keys decide the horizontal speed and which way we face.
        #    Only on_update sets change_x, so nothing else can fight over it.
        if self.left_pressed:
            self.player.change_x = -PLAYER_SPEED
            self.player.texture = self.left_texture
        elif self.right_pressed:
            self.player.change_x = PLAYER_SPEED
            self.player.texture = self.right_texture
        else:
            # No key held: stop, but keep facing the way we last moved.
            self.player.change_x = 0

        # 2. The engine moves the player and handles gravity and collisions.
        self.physics_engine.update()

        # 3. Reveal hidden tiles the player touched. Moving a tile to
        #    floor_list makes it drawn and solid in one step.
        touched_tiles = arcade.check_for_collision_with_list(
            self.player, self.hidden_list
        )
        for tile in touched_tiles:
            self.hidden_list.remove(tile)
            self.floor_list.append(tile)

        # 4. Fell out of the world: back to the start. Reset the vertical
        #    speed too, or the player returns still falling at full speed.
        #    Only the player moves; revealed tiles stay revealed.
        if self.player.center_y < FALL_LIMIT:
            self.player.position = self.spawn_point
            self.player.change_y = 0

        # 5. Reached the goal?
        if arcade.check_for_collision_with_list(self.player, self.goal_list):
            self.won = True
            print("You win!")

    def on_draw(self):
        # Wipe the previous frame, then draw back to front.
        self.clear()

        self.floor_list.draw()
        self.goal_list.draw()
        self.player_list.draw()
        # hidden_list is never drawn: that's what makes the tiles hidden.

    # -----------------------------------------------------------------------
    # Input
    # -----------------------------------------------------------------------

    def on_key_press(self, key, modifiers):
        # Left/right only record that a key is held; on_update acts on it.
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

        # Jumping is a one-time event, not a held state. can_jump() also
        # enforces the double-jump limit set in setup().
        elif key == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.physics_engine.jump(PLAYER_JUMP_SPEED)

        # Restart the level.
        elif key == arcade.key.R:
            self.setup()

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