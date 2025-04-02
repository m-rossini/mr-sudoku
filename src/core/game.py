import logging
from typing import List, Dict
from core.generator import SudokuGenerator
from core.difficulty import Difficulty

logger = logging.getLogger(__name__)
class SudokuGame:
    """Core game logic for Sudoku."""
    
    def __init__(self, generators: Dict[Difficulty, SudokuGenerator]):
        """Initialize a new game with a dictionary of generators."""
        self.generators = generators
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.original_board = [[0 for _ in range(9)] for _ in range(9)]
        self.solved_board = [[0 for _ in range(9)] for _ in range(9)]
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
    
    def new_game(self, difficulty: Difficulty):
        """Generate a new Sudoku puzzle based on the difficulty."""
        self.board, self.solved_board = self.generators[difficulty].generate(difficulty.name)
        self.original_board = [row[:] for row in self.board]
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
    
    def get_board(self) -> List[List[int]]:
        """Return the current board state."""
        return self.board
    
    def get_notes(self) -> List[List[set]]:
        """Return the current notes state."""
        return self.notes   
    
    def is_fixed_cell(self, row: int, col: int) -> bool:
        """Check if a cell is part of the original puzzle."""
        return self.original_board[row][col] != 0
    
    def set_cell(self, row: int, col: int, value: int):
        """Set a cell value if it's not fixed."""
        if not self.is_fixed_cell(row, col):
            self.board[row][col] = value
            self.notes[row][col].clear()
    
    def toggle_note(self, row: int, col: int, value: int):
        """Toggle a note on a cell."""
        if self.is_fixed_cell(row, col):
            return
        
        if value in self.notes[row][col]:
            self.notes[row][col].remove(value)
        else:
            self.notes[row][col].add(value)

    def is_board_valid(self) -> bool:
        """Check if the current board state is valid."""
        for row in range(9):
            for col in range(9):
                value = self.board[row][col]
                if value != 0:
                    # Temporarily empty the cell to avoid self-check
                    self.board[row][col] = 0
                    if not self.is_valid_move(row, col, value):
                        self.board[row][col] = value
                        return False
                    # Restore the cell value
                    self.board[row][col] = value
        return True
    
    def is_complete(self) -> bool:
        """Check if the puzzle is solved correctly."""
        for row in self.board:
            if 0 in row:
                return False
        
        return self.is_board_valid()
    
    def solve(self) -> bool:
        """Solve the current puzzle state."""
        # Implement a solving algorithm (backtracking)
        pass

    def is_valid_move(self, row: int, col: int, value: int) -> bool:
        """
        Check if placing value at the specified position would be a valid move.
        
        Args:
            row: Row index (0-8)
            col: Column index (0-8)
            value: Number to check (1-9)
            
        Returns:
            bool: True if the move is valid, False otherwise
        """
        # Skip validation for empty cells (value 0)
        if value == 0:
            return True
        
        logger.debug(f"Checking move: row={row}, col={col}, value={value} vs original board value={self.original_board[row][col]}")
        #let's check if the value is in the same position in the solved board
        if value == self.solved_board[row][col]:
            return True
        
        return False

    def is_permitted_move(self, row: int, col: int, value: int) -> bool:
        """
        Check if placing value at the specified position would be a permitted move.
        Permitted moves are different from valid moves in that they don't check the solved board. 
        
        Args:
            row: Row index (0-8)
            col: Column index (0-8)
            value: Number to check (1-9)
            
        Returns:
            bool: True if the move is permitted, False otherwise
        """
        # Check row
        for c in range(9):
            if c != col and self.board[row][c] == value:
                return False
        
        # Check column
        for r in range(9):
            if r != row and self.board[r][col] == value:
                return False
        
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r != row or c != col) and self.board[r][c] == value:
                    return False
        
        # If we get here, the move is permitted
        return True