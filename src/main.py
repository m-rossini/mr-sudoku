"""
Mr. Sudoku - Main entry point (Tkinter version)
"""
import sys
import tkinter as tk
from pathlib import Path

# Add the parent directory to sys.path if running as script
if __name__ == "__main__":
    parent_dir = Path(__file__).resolve().parent.parent
    if (parent_dir not in sys.path):
        sys.path.insert(0, str(parent_dir))

# Import game components
from core.game import SudokuGame
from ui.game_window import SudokuGameWindow
from core.generator import SimpleSudokuGenerator
from core.difficulty import Difficulty
from core.game_controller import GameController


def main():
    """Main entry point for the Sudoku game."""
    try:
        # Create the root window
        root = tk.Tk()
        root.title("Mr. Sudoku")
        
        # Create game logic with a dictionary of generators
        generators = {
            Difficulty.EASY: SimpleSudokuGenerator(),
            Difficulty.MEDIUM: SimpleSudokuGenerator(),
            Difficulty.HARD: SimpleSudokuGenerator()
        }
        game = SudokuGame(generators)
        
        window = SudokuGameWindow(root)  
        controller = GameController(game, window)
        
        # Start the Tkinter event loop
        root.mainloop()
        return 0
    except Exception as e:
        print(f"Error starting game: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())