"""Module execution entrypoint: python3 -m optical_compiler."""

import os
from pathlib import Path
import sys


def _boot() -> int:
    repo_venv_py = Path(__file__).resolve().parent.parent / ".venv" / "bin" / "python"
    if (
        sys.prefix == sys.base_prefix
        and repo_venv_py.is_file()
        and os.environ.get("OPTICAL_COMPILER_VENV_BOOTSTRAPPED") != "1"
    ):
        env = {**os.environ, "OPTICAL_COMPILER_VENV_BOOTSTRAPPED": "1"}
        os.execve(str(repo_venv_py), [str(repo_venv_py), "-m", "optical_compiler", *sys.argv[1:]], env)
    from .cli import main

    return main()


if __name__ == "__main__":
    sys.exit(_boot())
