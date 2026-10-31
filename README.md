# Little Yellow

A hidden-platform puzzle platformer. You play a small yellow cube in a world where most of the platforms are invisible. Get close to a hidden tile and it appears, so you can feel your way through each level to the spinning gold square at the end.

Made with Python and [Arcade](https://api.arcade.academy), with levels built in [Tiled](https://www.mapeditor.org)

## Play it (Windows)

1. Go to the [latest release](https://github.com/NxtCreator/little-yellow/releases/tag/v1.0.0) and download `LittleYellow-windows-v1.0.0.zip`.
2. **Unzip the whole folder.** Don't run the game from inside the zip, and don't move `LittleYellow.exe` out on its own, because it needs the files next to it.
3. Run `LittleYellow.exe`.

Windows may say it doesn't recognize the app, because it isn't signed. Click **More info**, then **Run anyway**.

## How to play

- Walk and jump to the spinning gold square to finish the level.
- Hidden platforms appear when you get close to them. If a path looks empty, walk toward it.
- You get one jump on the ground and one extra jump in the air.
- If you fall off the world, you respawn at the start of the level. Tiles you've already revealed stay revealed.
- After you win, you can go to the next level or restart.

## Controls

| Key | Action |
| --- | --- |
| Left / Right arrows | Move |
| Up arrow | Jump (press again in the air for a second jump) |
| R | Restart the current level |
| N | Next level (after winning) |
| F11 | Toggle fullscreen |

The window can also be resized by dragging its edges.

## Run it from source

You'll need Python 3.10 or newer.

```
git clone https://github.com/NxtCreator/little-yellow.git
cd little-yellow
python -m venv .venv
```

Activate the virtual environment:

- Linux / macOS: `source .venv/bin/activate`
- Windows: `.venv\Scripts\activate`

Then install the requirements and start the game:

```
pip install -r requirements.txt
python main.py
```

## Build the Windows .exe

PyInstaller can only build for the system it's running on, so this repo has a GitHub Actions workflow that builds the Windows version in the cloud:

1. Open the **Actions** tab and choose **Build Windows exe**.
2. Click **Run workflow**.
3. When it finishes, download the `LittleYellow-windows` artifact from the run page.

To build locally instead, run this on the system you want to build for (use `:` instead of `;` on Linux and macOS):

```
pip install pyinstaller
pyinstaller main.py --name LittleYellow --add-data "assets;assets"
```

## Making your own levels

Levels are Tiled maps stored in `assets/`. Each map needs four tile layers with these exact names:

| Layer | What it's for |
| --- | --- |
| `Platforms` | Solid tiles that are visible from the start |
| `Hidden` | Tiles that stay invisible until the player gets close |
| `Spawn` | One tile marking where the player starts |
| `Goal` | One tile marking where the goal sits |

Keep layer offsets at 0, export the map as JSON (for example `assets/level4.json`), and add its path to the `LEVELS` list at the top of `main.py`.

## Project layout

```
main.py                     the whole game
assets/                     images and Tiled maps
requirements.txt            Python dependencies
.github/workflows/          the Windows build workflow
```

## Credits
- Code, art, and levels by me.
