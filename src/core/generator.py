from abc import ABC, abstractmethod
from typing import List

class SudokuGenerator(ABC):
    """Abstract base class for Sudoku puzzle generators."""
    
    @abstractmethod
    def generate(self, difficulty: str) -> tuple[List[List[int]], List[List[int]]]:
        """Generate a new Sudoku puzzle based on the difficulty."""
        pass

class FixedBoardSudokuGenerator(SudokuGenerator):
    """A simple Sudoku puzzle generator implementation."""
    
    def generate(self, difficulty: str) -> tuple[List[List[int]], List[List[int]]]:
        """Generate a new Sudoku puzzle based on the difficulty."""
        unsolved_board = [
                    [0, 9, 3, 0, 0, 8, 4, 0, 0],
                    [0, 0, 1, 0, 0, 0, 0, 0, 0],
                    [0, 0, 7, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 3, 4, 7, 0, 0],
                    [0, 6, 0, 0, 1, 0, 0, 0, 0],
                    [0, 4, 0, 0, 0, 0, 0, 5, 0],
                    [0, 0, 4, 0, 0, 0, 2, 0, 0],
                    [0, 0, 0, 4, 0, 0, 0, 3, 0],
                    [0, 3, 6, 0, 0, 0, 0, 0, 4]
                ]
        
        solved_board = [
                    [5, 9, 3, 6, 7, 8, 4, 1, 2],
                    [6, 2, 1, 5, 4, 3, 8, 7, 9],
                    [4, 8, 7, 1, 2, 9, 3, 6, 5],
                    [1, 5, 2, 9, 3, 4, 7, 8, 6],
                    [3, 6, 9, 8, 1, 7, 5, 2, 4],
                    [7, 4, 8, 2, 6, 5, 9, 5, 3],
                    [9, 7, 4, 3, 5, 6, 2, 4, 8],
                    [2, 1, 5, 4, 8, 2, 6, 3, 7],
                    [8, 3, 6, 7, 9, 1, 3, 5, 4]
                ]

        return  (unsolved_board, solved_board)
