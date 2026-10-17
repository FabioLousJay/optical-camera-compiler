"""CLI entry point for `python -m photopipe`."""

import os
from pathlib import Path
import sys


def _boot() -> None:
    repo_venv_py = Path(__file__).resolve().parent.parent / ".venv" / "bin" / "python"
    if (
        sys.prefix == sys.base_prefix
        and repo_venv_py.is_file()
        and os.environ.get("PHOTOPIPE_VENV_BOOTSTRAPPED") != "1"
    ):
        env = {**os.environ, "PHOTOPIPE_VENV_BOOTSTRAPPED": "1"}
        os.execve(str(repo_venv_py), [str(repo_venv_py), "-m", "photopipe", *sys.argv[1:]], env)
    from photonqc.cli import main

    main()


if __name__ == "__main__":
    _boot()
