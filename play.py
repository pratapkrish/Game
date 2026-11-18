"""One-command launcher for Ram's Mario. Requires Python, internet on first run."""
import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV = ROOT / ".game-env"
GAME = ROOT / "game.py"


def python_in_env():
    if os.name == "nt":
        return ENV / "Scripts" / "python.exe"
    return ENV / "bin" / "python"


def run_command(args):
    subprocess.check_call([str(a) for a in args], cwd=str(ROOT))


def main():
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print("Ram's Mario supports Python 3.8 to 3.14 on common Mac/Windows systems.")
        print("Please install a current Python 3 release from python.org.")
        return 1

    if version.minor == 8:
        package = "pygame==2.6.1"
    elif version.minor == 9:
        package = "pygame-ce==2.5.6"
    else:
        package = "pygame-ce>=2.5.6,<3"

    py = python_in_env()
    if not py.exists():
        print("Setting up game for Python {}.{} (first launch only)...".format(version.major, version.minor), flush=True)
        try:
            venv.EnvBuilder(with_pip=True).create(str(ENV))
        except Exception as error:
            print("Couldn't create the game environment: {}".format(error))
            print("Your Python installation may need the venv module.")
            return 1

    check = subprocess.run([str(py), "-c", "import pygame"], cwd=str(ROOT),
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if check.returncode != 0:
        print("Installing a compatible game library (first launch only)...", flush=True)
        try:
            run_command([py, "-m", "pip", "install", "--only-binary=:all:", package])
        except subprocess.CalledProcessError:
            print("\nCouldn't find a ready-made Pygame package for this Python/OS combination.")
            print("Try Python 3.12 or 3.13 from python.org, then run play.py again.")
            return 1

    print("Launching Ram's Mario...", flush=True)
    try:
        run_command([py, GAME])
    except subprocess.CalledProcessError as error:
        return error.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
