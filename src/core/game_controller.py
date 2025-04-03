import time
import logging
from core.game import SudokuGame
from core.difficulty import Difficulty
from core.stats import GameStats
from ui.game_window import SudokuGameWindow

logger = logging.getLogger(__name__)
class GameController:
    """Controller to manage the game logic and UI interaction."""
    
    # Maximum number of wrong moves allowed
    MAX_WRONG_MOVES = 3
    
    # Constant to indicate game over state
    GAME_OVER = -1

    def __init__(self, game: SudokuGame, window: SudokuGameWindow):
        self.game = game
        self.window = window
        self.wrong_moves = 0
        self.stats = GameStats()
        self.note_mode = False
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
    
    def start_new_game(self, difficulty: Difficulty):
        """Start a new game with the given difficulty."""
        logger.debug(f">>>Starting new game with difficulty: {difficulty.value}")
        self.start_time = time.time()
        self.game.new_game(difficulty)
        self.reset_wrong_moves()
        
        # Reset notes when starting a new game
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        
        self.stats.stats[difficulty][GameStats.GAMES_PLAYED] += 1
        self.window.update_board()
    
    def set_cell_value(self, row: int, col: int, value: int):
        """Set the value of a cell in the game."""
        logger.debug(f">>>GameController::set_cell_value - Setting value {value} at ({row}, {col}), note_mode={self.note_mode}")
        
        if self.note_mode:
            self.toggle_note(row, col, value)
        else:
            # Normal mode - set the cell value
            if self.game.is_fixed_cell(row, col):
                logger.debug(f">>>GameController::set_cell_value - Cell ({row}, {col}) is fixed, ignoring input")
                return
                
            previous_value = self.game.get_board()[row][col]
            self.game.set_cell(row, col, value)
            
            # Clear notes when setting a cell value
            self.notes[row][col].clear()
            
            logger.debug(f">>>GameController::set_cell_value - Changed value from {previous_value} to {value}")

        # Force a complete board update to ensure UI is consistent
        self.window.update_board()
    
    def toggle_note(self, row: int, col: int, value: int):
        """Toggle a note on a cell."""
        if self.game.is_fixed_cell(row, col):
            return
        
        logger.debug(f">>>Toggling note {value} at position ({row}, {col})")
        
        if value in self.notes[row][col]:
            self.notes[row][col].remove(value)
        else:
            self.notes[row][col].add(value)
    
    def clear_notes(self, row: int, col: int):
        """Clear the notes for a cell."""
        logger.debug(f">>>Clearing notes at position ({row}, {col})")
        self.notes[row][col].clear()
        self.window.update_board()
    
    def get_notes(self):
        """Get the current notes state."""
        return self.notes

    def check_solution(self):
        """Check if the current board state is valid."""
        if self.game.is_board_valid():
            if self.game.is_complete():
                self.window.show_message("Success", "The puzzle is solved correctly!")
                self.update_stats(True)
            else:
                self.window.show_message("Valid", "So far, so good. Keep going!")
        else:
            self.window.show_message("Error", "There are conflicts on the board.")
    
    def is_game_complete(self) -> bool:
        """Check if the game is complete."""
        return self.game.is_complete()
    
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
            self.update_stats(True)
        else:
            self.window.show_message("Error", "This puzzle cannot be solved!")
    
    def wrong_move_done(self):
        """Increment the wrong moves counter and check for game over."""
        self.wrong_moves += 1
        return (self.is_game_over(),self.wrong_moves,self.MAX_WRONG_MOVES)
    
    def is_game_over(self) -> bool:
        """Check if the game is over due to too many wrong moves."""
        return self.wrong_moves >= self.MAX_WRONG_MOVES
    
    def is_valid_move(self, row: int, col: int, value: int) -> bool:
        """Check if the given move is valid for normal mode and permitted for notes."""
        if self.note_mode:
            return self.game.is_permitted_move(row, col, value)
        else:
            return  self.game.is_valid_move(row, col, value)
        
    def reset_wrong_moves(self):
        """Reset the wrong moves counter."""
        self.wrong_moves = 0

    def update_stat(self, difficulty: Difficulty, stat: str, value: int):
        """Update a specific statistic for the given difficulty."""
        current_value = self.stats.stats[difficulty][stat]
        self.stats.stats[difficulty][stat] = current_value + value

    def update_stats(self, won: bool):
        """Update the stats for the current game."""
        difficulty = Difficulty(self.window.difficulty.get())
        time_taken = time.time() - self.start_time
        moves = sum(sum(1 for cell in row if cell != 0) for row in self.game.get_board())
        self.stats.update_stats(difficulty, won, moves, self.wrong_moves, time_taken)
    
    def get_stats(self, difficulty: Difficulty) -> dict[str, int]:
        """Return the stats for the given difficulty level."""
        return self.stats.get_stats(difficulty)
    
    def save_stats(self):
        """Save the game statistics to a file."""
        self.stats.save_stats()

    def set_note_mode(self, note_mode: bool):
        """Set the note mode."""
        self.note_mode = note_mode
        logger.debug(f">>>Note mode is now: {self.note_mode}")

    def generate_auto_notes(self):
        """
        Generate automatic notes for all empty cells.
        This calculates possible values for each empty cell.
        """
        logger.debug(">>>Generating auto notes for all empty cells")
        
        # Clear all existing notes
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        
        # Generate new notes for all empty cells
        board = self.game.get_board()
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:  # Only for empty cells
                    possible_values = self.game.calculate_possible_values(row, col)
                    self.notes[row][col] = possible_values
        
        # Update the display
        self.window.update_board()
