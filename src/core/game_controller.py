from core.game import SudokuGame
from core.difficulty import Difficulty
from core.stats import GameStats
from ui.game_window import SudokuGameWindow
import time

class GameController:
    """Controller to manage the game logic and UI interaction."""
    
    # Maximum number of wrong moves allowed
    MAX_WRONG_MOVES = 3
    
    # Constant to indicate game over state
    GAME_OVER = -1

    def __init__(self, game: SudokuGame, window: SudokuGameWindow):
        self.game = game
        self.window = window
        self.window.set_controller(self)
        self.wrong_moves = 0
        self.stats = GameStats()
        self.start_new_game(Difficulty.MEDIUM)
        self.note_mode = False
    
    def start_new_game(self, difficulty: Difficulty):
        """Start a new game with the given difficulty."""
        self.start_time = time.time()
        self.game.new_game(difficulty)
        self.reset_wrong_moves()
        self.stats.stats[difficulty][GameStats.GAMES_PLAYED] += 1
        self.window.update_board()
    
    def set_cell_value(self, row: int, col: int, value: int):
        """Set the value of a cell in the game."""
        if self.note_mode:
            self.game.toggle_note(row, col, value)
        else:
            self.game.set_cell(row, col, value)

        self.window.update_board()
    
    def clear_notes(self, row: int, col: int):
        """Clear the notes for a cell."""
        self.game.notes[row][col].clear()
        self.window.update_board()

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
    
    def get_notes(self):
        """Get the current notes state."""
        return self.game.get_notes()
    
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
        print(f"Note mode is now: {self.note_mode}")
