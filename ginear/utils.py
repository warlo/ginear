# /usr/bin/env python3
from pathlib import Path

from dotenv import set_key, unset_key

DOTFILE_PATH = Path.home() / ".ginear"


def write_to_env(key: str, value: str) -> None:
    set_key(DOTFILE_PATH, key, value)


def clear_env_key(key: str) -> None:
    unset_key(DOTFILE_PATH, key)


def switch_branch(branch_name: str) -> None:
    import subprocess

    try:
        subprocess.run(["git", "switch", "-c", branch_name], check=True)
        print(f"Created and switched to branch '{branch_name}' successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
