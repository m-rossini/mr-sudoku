"""
Mr. Sudoku - Main entry point (Tkinter version)
"""

import sys
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import argparse
import logging

# Add the parent directory to sys.path if running as script
if __name__ == "__main__":
    parent_dir = Path(__file__).resolve().parent.parent
    if parent_dir not in sys.path:
        sys.path.insert(0, str(parent_dir))

from core.ui_components import UIManager

# Update the import to use our new generator
from core.game import BacktrackingSudokuGenerator, SimpleSudokuSolver, GameEngine
from core.controller import GameController

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the Sudoku game."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Mr. Sudoku - Tkinter version")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)",
    )
    args = parser.parse_args()

    logging.getLogger().setLevel(args.log_level)
    logger.info(f"Setting log level to {args.log_level}")

    try:
        # Create the root window
        root = tk.Tk()
        root.title("Mr. Sudoku")

        # Set up the window close protocol
        root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))

        # Initialize components for the root window
        game_engine = _initialize_components(root)

        # Start the Tkinter event loop
        root.mainloop()
        return 0
    except Exception as e:
        logger.critical(f"Error starting game: {e}", exc_info=True)
        return 1


def on_closing(root):
    """
    Handle window close event by asking for confirmation.

    Args:
        root: The root window
    """
    logger.debug(">>>Main::on_closing - User attempted to close the game")

    if messagebox.askyesno("Quit", "Are you sure you want to quit the game?"):
        logger.info("User confirmed exit. Closing game.")
        # Perform any cleanup needed here (save game state, etc.)
        root.destroy()
    else:
        logger.debug(">>>Main::on_closing - User canceled exit")


def _initialize_components(root):
    """
    Initialize components for the root window.

    Args:
        root: The root window

    Returns:
        GameController: The initialized game controller
    """
    logger.debug(
        ">>>Main::initialize_components - Initializing components for the whole game"
    )

    # Use the BacktrackingSudokuGenerator instead of FixedBoardSudokuGenerator
    generator = BacktrackingSudokuGenerator()
    solver = SimpleSudokuSolver()
    engine = GameEngine(generator, solver)
    uimanager = UIManager(root, on_closing)  # Pass on_closing as a dependency
    controller = GameController(engine, uimanager)

    controller.start_game(uimanager.get_difficulty())
    return controller


if __name__ == "__main__":
    sys.exit(main())
