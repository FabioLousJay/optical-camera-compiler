"""Module execution entrypoint: python3 -m optical_compiler."""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
