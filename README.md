# Ram's Mario 🎮

A Mario-inspired platform game built with Python. Collect coins, jump over obstacles, and reach the flagpole before you run out of your **3 lives**!

## How to play (Terminal only, no VS Code)

You need **Python 3** installed. If you don't have it, download it from [python.org](https://www.python.org/downloads/). The first time you play, you'll need an internet connection to install the game library.

### Mac

1. On GitHub, click **Code → Download ZIP**, then double-click the ZIP to unzip it.
2. Open **Terminal** (press **Command + Space**, type `Terminal`, press Enter).
3. Type `cd ` (with a space after `cd`), then **drag the unzipped `rams_mario` folder into Terminal** and press Enter.
4. **Install the game library** by copying this into Terminal and pressing Enter:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

5. **Start the game**:

   ```bash
   python3 game.py
   ```

### Windows

1. On GitHub, click **Code → Download ZIP**, then right-click the ZIP and choose **Extract All**.
2. Open the extracted **`rams_mario` folder** in File Explorer (the folder containing `game.py`).
3. Click the **address bar** at the top of File Explorer, type `cmd`, and press Enter. Command Prompt will open in the correct folder.
4. **Install the game library** by copying this into Command Prompt and pressing Enter:

   ```bat
   py -m pip install -r requirements.txt
   ```

5. **Start the game**:

   ```bat
   py game.py
   ```

**That's it!** A game window will open. Press **Enter** to begin. You only have to install the library once.

## Controls

| Key | Action |
| --- | --- |
| **A / Left Arrow** | Move left |
| **D / Right Arrow** | Move right |
| **Space / W / Up Arrow** | Jump (hold longer to jump higher) |
| **Enter** | Start |
| **R or Enter** | Restart after Game Over or Victory |

## Game rules

- You get **3 lives** to complete the level.
- Collect coins, stomp enemies, and grab mushrooms.
- If you lose a life, you respawn on safe ground near where you died and keep your score.
- Lose all 3 lives and you'll see **GAME OVER**. Press **R** or **Enter** to play again.
- Reach the flagpole to win!

## If something doesn't work

- **`python3` or `py` is not recognized:** Install Python 3 from [python.org](https://www.python.org/downloads/) and reopen Terminal/Command Prompt. On Windows, select **Add Python to PATH** if offered.
- **`No such file` / `can't open game.py`:** You are probably in the wrong folder. Repeat the step that opens Terminal/Command Prompt in the `rams_mario` folder.
- **Pygame installation error:** Run the installation command again while connected to the internet. The `requirements.txt` file picks a version based on Python. Some very old or brand-new Python versions may not have a prebuilt Pygame package for your computer; Python 3.12 or 3.13 is a good fallback.

*No code editor or IDE is needed.*
