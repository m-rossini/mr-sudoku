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
                        [5, 3, 0, 6, 7, 8, 9, 1, 0],
                        [6, 7, 2, 1, 9, 5, 3, 4, 8],
                        [1, 9, 8, 0, 4, 2, 5, 6, 7],
                        [8, 5, 9, 7, 0, 1, 4, 2, 0],
                        [4, 2, 6, 8, 5, 3, 0, 9, 1],
                        [7, 1, 3, 9, 2, 4, 8, 0, 6],
                        [9, 6, 1, 5, 3, 0, 2, 8, 4],
                        [2, 8, 7, 4, 1, 9, 6, 3, 5],
                        [3, 4, 5, 2, 8, 6, 1, 7, 9]
                ]
        
        solved_board = [
                        [5, 3, 4, 6, 7, 8, 9, 1, 2],
                        [6, 7, 2, 1, 9, 5, 3, 4, 8],
                        [1, 9, 8, 3, 4, 2, 5, 6, 7],
                        [8, 5, 9, 7, 6, 1, 4, 2, 3],
                        [4, 2, 6, 8, 5, 3, 7, 9, 1],
                        [7, 1, 3, 9, 2, 4, 8, 5, 6],
                        [9, 6, 1, 5, 3, 7, 2, 8, 4],
                        [2, 8, 7, 4, 1, 9, 6, 3, 5],
                        [3, 4, 5, 2, 8, 6, 1, 7, 9]
                ]

        return  (unsolved_board, solved_board)
