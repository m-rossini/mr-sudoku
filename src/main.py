"""
Mr. Sudoku - Main entry point (Tkinter version)
"""
import sys
import tkinter as tk
from pathlib import Path
import argparse
import logging

# Add the parent directory to sys.path if running as script
if __name__ == "__main__":
    parent_dir = Path(__file__).resolve().parent.parent
    if (parent_dir not in sys.path):
        sys.path.insert(0, str(parent_dir))

# Import game components
from core.game import SudokuGame
from ui.game_window import SudokuGameWindow
from core.generator import FixedBoardSudokuGenerator
from core.difficulty import Difficulty
from core.game_controller import GameController

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
        
        # Create game logic with a dictionary of generators
        generators = {
            Difficulty.EASY: FixedBoardSudokuGenerator(),
            Difficulty.MEDIUM: FixedBoardSudokuGenerator(),
            Difficulty.HARD: FixedBoardSudokuGenerator()
        }
        game = SudokuGame(generators)
        
        window = SudokuGameWindow(root)  
        controller = GameController(game, window)
        
        # Start the Tkinter event loop
        root.mainloop()
        return 0
    except Exception as e:
        logger.critical(f"Error starting game: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())