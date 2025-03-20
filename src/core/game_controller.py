from core.game import SudokuGame
from core.difficulty import Difficulty
from ui.game_window import SudokuGameWindow

class GameController:
    """Controller to manage the game logic and UI interaction."""
    
    def __init__(self, game: SudokuGame, window: SudokuGameWindow):
        self.game = game
        self.window = window
        self.window.set_controller(self)
        self.start_new_game(Difficulty.MEDIUM)
    
    def start_new_game(self, difficulty: Difficulty):
        """Start a new game with the given difficulty."""
        self.game.new_game(difficulty)
        self.window.update_board()
    
    def set_cell_value(self, row: int, col: int, value: int):
        """Set the value of a cell in the game."""
        self.game.set_cell(row, col, value)
        self.window.update_board()
    
    def check_solution(self):
        """Check if the current board state is valid."""
        if self.game.check_board():
            if self.game.is_complete():
                self.window.show_message("Success", "The puzzle is solved correctly!")
            else:
                self.window.show_message("Valid", "So far, so good. Keep going!")
        else:
            self.window.show_message("Error", "There are conflicts on the board.")
    
    def get_board(self):
        """Get the current board state."""
        return self.game.get_board()
    
    def is_fixed_cell(self, row: int, col: int) -> bool:
        """Check if a cell is part of the original puzzle."""
        return self.game.is_fixed_cell(row, col)
    
    def solve_game(self):
        """Request the game model to solve the puzzle."""
        if self.game.solve():
            self.window.update_board()
            self.window.show_message("Solved", "Puzzle solved successfully!")
        else:
            self.window.show_message("Error", "This puzzle cannot be solved!")
