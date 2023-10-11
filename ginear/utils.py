# /usr/bin/env python3
from pathlib import Path

DOTFILE_PATH = Path.home() / ".ginear"


def write_to_env(key: str, value: str) -> None:
    with open(DOTFILE_PATH, "a") as env_file:
        env_file.write(f"\n{key}={value}\n")


def switch_branch(branch_name: str) -> None:
    import subprocess

    try:
        subprocess.run(["git", "switch", "-c", branch_name], check=True)
        print(f"Created and switched to branch '{branch_name}' successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
