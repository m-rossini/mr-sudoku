from abc import ABC, abstractmethod
from typing import List

class SudokuGenerator(ABC):
    """Abstract base class for Sudoku puzzle generators."""
    
    @abstractmethod
    def generate(self, difficulty: str) -> List[List[int]]:
        """Generate a new Sudoku puzzle based on the difficulty."""
        pass

class SimpleSudokuGenerator(SudokuGenerator):
    """A simple Sudoku puzzle generator implementation."""
    
    def generate(self, difficulty: str) -> List[List[int]]:
        """Generate a new Sudoku puzzle based on the difficulty."""
        print(f"In generator itself.Generating new {difficulty} puzzle")
        board1 = [
                [0,2,1,5,3,0,6,0,0],
                [0,0,0,0,0,6,7,0,0],
                [8,0,0,0,0,4,0,0,2],
                [0,9,2,0,0,0,0,4,0],
                [0,0,0,0,8,2,0,0,5],
                [3,0,0,4,7,0,0,9,0],
                [2,6,9,0,0,1,0,0,8],
                [0,5,7,0,4,0,3,0,0],
                [0,0,0,2,0,0,0,0,1]
                ]
        
        return  board1
