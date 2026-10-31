import os
import sys
import math
import arcade

if getattr(sys, "frozen", False):
    os.chdir(sys._MEIPASS)

# ---------------------------------------------------------------------------
# GAME CONSTANTS
# ---------------------------------------------------------------------------

# Window
WIDTH = 800
HEIGHT = 600
TITLE = "Little Yellow"

# Sizes (the player is smaller than a platform square on purpose)
TILE_SIZE = 48
PLAYER_SIZE = 36
PLAYER_ART_SIZE = 24 # the size of the player PNGs
REVEAL_RANGE = TILE_SIZE / 3

LEVELS = [
    "assets/level1.json",
    "assets/level2.json"
]

# Movement and physics
GRAVITY = 1
PLAYER_SPEED = 6
PLAYER_JUMP_SPEED = 16
MAX_JUMPS = 2          # 2 = one jump plus one extra jump in mid-air
FALL_LIMIT = -200      # below this y, the player has fallen out of the world
PLAYER_ACCELERATION = 0.3
PLAYER_FRICTION = 0.1


class Game(arcade.Window):
    """Main game class: owns the window, the level, and the game loop."""

    # -----------------------------------------------------------------------
    # Setup
    # -----------------------------------------------------------------------

    def __init__(self):
        super().__init__(WIDTH, HEIGHT, TITLE)
        self.background_color = arcade.csscolor.BLACK
        self.gui_camera = None
        self.win_text = None
        self.hint_text = None
        self.level_index = 0

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

        self.camera = None

        # Level state
        self.spawn_point = None
        self.won = False

        # Keys currently held. on_update turns these into movement.
        self.left_pressed = False
        self.right_pressed = False

    def setup(self):
        """Build the level. Call it again to restart."""
        self.won = False

        # load a map
        tile_map = arcade.load_tilemap(LEVELS[self.level_index], scaling=1.0)

        # Brand-new lists every time, so a restart never piles
        # new tiles on top of the old ones.
        self.player_list = arcade.SpriteList()
        self.floor_list = tile_map.sprite_lists["Platforms"]
        self.hidden_list = tile_map.sprite_lists["Hidden"]
        self.goal_list = arcade.SpriteList()

        self.left_texture = arcade.load_texture("assets/little_yellow_left.png")
        self.right_texture = arcade.load_texture("assets/little_yellow_right.png")

        self.gui_camera = arcade.Camera2D()
        self.win_text = arcade.Text(
            "You win!", WIDTH / 2, HEIGHT / 2, arcade.color.WHITE, 40, anchor_x="center"
        )

        self.hint_text = arcade.Text(
            "Hit 'N' to go to the next level " \
            "or 'R' to restart level", WIDTH / 2, HEIGHT / 2 - 30, arcade.color.WHITE, 20, anchor_x="center"
        )

        # --- Player ---
        self.player = arcade.Sprite(self.right_texture, scale=PLAYER_SIZE / PLAYER_ART_SIZE)
        self.player_list.append(self.player)
        # start where the spawn marker was painted
        spawn_marker = tile_map.sprite_lists["Spawn"][0]
        self.player.position = spawn_marker.position
        # Where to come back to after falling out of the world.
        self.spawn_point = self.player.position

        # --- Goal ---
        goal_marker = tile_map.sprite_lists["Goal"][0]
        goal = arcade.SpriteSolidColor(TILE_SIZE, TILE_SIZE, color=arcade.csscolor.BLUE_VIOLET)
        goal.position = goal_marker.position
        self.goal_list.append(goal)

        # --- Physics ---
        # Created last, because it needs the player and the floor to exist.
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            walls=self.floor_list,
            gravity_constant=GRAVITY,
        )
        self.physics_engine.enable_multi_jump(MAX_JUMPS)

        # create a camera
        self.camera = arcade.Camera2D()  

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
        target_speed = 0
        if self.left_pressed and self.right_pressed:
            target_speed = 0
        elif self.left_pressed:
            target_speed = -PLAYER_SPEED
            self.player.texture = self.left_texture
        elif self.right_pressed:
            target_speed = PLAYER_SPEED
            self.player.texture = self.right_texture

        # Slide to stop when no key  is help, speed-up otherwise
        step = PLAYER_FRICTION if target_speed == 0 else PLAYER_ACCELERATION

        if self.player.change_x < target_speed:
            self.player.change_x = min(self.player.change_x + step, target_speed)
        elif self.player.change_x > target_speed:
            self.player.change_x = max(self.player.change_x - step, target_speed)

        # 2. The engine moves the player and handles gravity and collisions.
        self.physics_engine.update()

        # 3. Reveal hidden tiles that are within range of the player.
        #   list(...) makes a copy, because we remove tiles while looping
        for tile in list(self.hidden_list):
            gap_x = max(tile.left - self.player.right, self.player.left - tile.right, 0)
            gap_y = max(tile.bottom - self.player.top, self.player.bottom - tile.top, 0)

            if gap_x <= REVEAL_RANGE and gap_y <= REVEAL_RANGE:
                self.hidden_list.remove(tile)
                self.floor_list.append((tile))

        # 4. Fell out of the world: back to the start. Reset the vertical
        #    speed too, or the player returns still falling at full speed.
        #    Only the player moves; revealed tiles stay revealed.
        if self.player.center_y < FALL_LIMIT:
            self.player.position = self.spawn_point
            self.player.change_y = 0

        # 5. Reached the goal?
        if arcade.check_for_collision_with_list(self.player, self.goal_list):
            self.won = True

        # camera follows player
        self.camera.position = self.player.position

    def on_draw(self):
        # Wipe the previous frame, then draw back to front.
        self.clear()

        self.camera.use()

        self.floor_list.draw()
        self.goal_list.draw()
        self.player_list.draw()

        self.gui_camera.use()

        if self.won:
            self.win_text.draw()
            self.hint_text.draw()

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

        # Go to next level
        elif key == arcade.key.N:
            if self.won and self.level_index < len(LEVELS) - 1:
                self.level_index += 1
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