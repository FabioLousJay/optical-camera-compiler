"""CLI: python -m photopipe [export|inspect|restore|evaluate|benchmark|calibrate] ..."""

from photonqc.cli import main

__all__ = ["main"]

if __name__ == "__main__":
    main()
