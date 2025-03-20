from typing import List, Dict
from core.generator import SudokuGenerator
from core.difficulty import Difficulty

class SudokuGame:
    """Core game logic for Sudoku."""
    
    def __init__(self, generators: Dict[Difficulty, SudokuGenerator]):
        """Initialize a new game with a dictionary of generators."""
        self.generators = generators

        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.original_board = [[0 for _ in range(9)] for _ in range(9)]
    
    def new_game(self, difficulty: Difficulty):
        """Generate a new Sudoku puzzle based on the difficulty."""
        print(f"SudokuGame::new_game::Generating new {difficulty.name} puzzle")
        self.board = self.generators[difficulty].generate(difficulty.name)
        print(f'board: {self.board}')
        self.original_board = [row[:] for row in self.board]
        print(f'original_board: {self.original_board}')
    
    def get_board(self) -> List[List[int]]:
        """Return the current board state."""
        return self.board
    
    def is_fixed_cell(self, row: int, col: int) -> bool:
        """Check if a cell is part of the original puzzle."""
        return self.original_board[row][col] != 0
    
    def set_cell(self, row: int, col: int, value: int):
        """Set a cell value if it's not fixed."""
        if not self.is_fixed_cell(row, col):
            self.board[row][col] = value
    
    def check_board(self) -> bool:
        """Check if the current board state is valid."""
        # Implement Sudoku validation logic
        pass
    
    def is_complete(self) -> bool:
        """Check if the puzzle is solved correctly."""
        # Check if board is full and valid
        pass
    
    def solve(self) -> bool:
        """Solve the current puzzle state."""
        # Implement a solving algorithm (backtracking)
        pass