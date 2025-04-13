from abc import ABC, abstractmethod
from typing import List
from core.controller import ControllerDependent
import logging

logger = logging.getLogger(__name__)


class GameEngine(ControllerDependent):
    def __init__(self, generator, solver):
        logger.debug(">>>GameEngine::init - Initializing GameEngine")
        self.generator = generator
        self.solver = solver

    def solve(self, board):
        """
        Solve the Sudoku puzzle.

        Args:
        board: The Sudoku board to be solved.

        Returns:
        List[List[int]]: The solved Sudoku board.
        """
        logger.debug(">>>GameEngine::solve - Solving the Sudoku puzzle")
        return self.solver.solve(board)
    
    def set_controller(self, controller):
        """
        Set the controller for this GameEngine.

        Args:
        controller: The controller instance.
        """
        logger.debug(">>>GameEngine::set_controller - Setting controller")
        self.controller = controller

    def start_game(self, difficulty):
        """
        Start the game by generating a new Sudoku puzzle.
        """
        logger.debug(">>>GameEngine::start_game - Starting new game")
        self._board, self._solution = self.generator.generate(difficulty)
        return self._board, self._solution

    def is_input_correct(self, _solution, row, col, value):
        """
        Check if the input value is correct for the given position.

        Args:
                _solution: The solution board.
                row: The row index.
                col: The column index.
                value: The value to be checked.

        Returns:
                bool: True if the input is correct, False otherwise.
        """
        logger.debug(f">>>GameEngine::is_input_correct - Checking input correctness at ({row}, {col}): {value}")
        if _solution[row][col] == value:
                return True
        else:
                return False


    def can_input(self, _board, row, col, value):
        """
        Check if a value can be input at the specified position.

        Args:
                row: The row index.
                col: The column index.
                value: The value to be checked.

        Returns:
                bool: True if the input is valid, False otherwise.
        """
        logger.debug(f">>>GameEngine::can_input - Checking input validity at ({row}, {col}): {value}")

        if _board[row][col] == 0:
            # Check if the value is not already in the same row
            for i in range(9):
                if _board[row][i] == value:
                    logger.debug(f">>>GameEngine::can_input - Value {value} already in row {row}")
                    return False

            # Check if the value is not already in the same column
            for i in range(9):
                if _board[i][col] == value:
                    logger.debug(f">>>GameEngine::can_input - Value {value} already in column {col}")
                    return False

            # Check if the value is not already in the same 3x3 box
            box_row_start = (row // 3) * 3
            box_col_start = (col // 3) * 3
            for i in range(box_row_start, box_row_start + 3):
                for j in range(box_col_start, box_col_start + 3):
                    if _board[i][j] == value:
                        logger.debug(f">>>GameEngine::can_input - Value {value} already in box ({box_row_start}, {box_col_start})")
                        return False

            # If all checks pass, the input is valid
            logger.debug(f">>>GameEngine::can_input - Input at ({row}, {col}) is valid")
            return True
        else:
            logger.debug(f">>>GameEngine::can_input - Cell at ({row}, {col}) is not empty")
            return False
    

class SudokuSolver(ABC):
    """Abstract base class for Sudoku puzzle generators."""

    @abstractmethod
    def solve(self, board: List[List[int]]):
        """Generate a new Sudoku puzzle based on the difficulty."""
        pass


class SimpleSudokuSolver(SudokuSolver):
    """A simple Sudoku solver implementation."""

    def solve(self, board: List[List[int]]) -> List[List[int]]:
        """Solve the Sudoku puzzle."""
        logger.debug(
            ">>>SimpleSudokuSolver::solve - Starting to solve the Sudoku puzzle"
        )
        return board


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

        logger.debug(f">>>FixedBoardSudokuGenerator::generate - Generating Sudoku puzzle with difficulty: {difficulty}")
        unsolved_board = [
            [3, 0, 6, 5, 0, 8, 4, 0, 0],
            [5, 2, 0, 0, 0, 0, 0, 0, 0],
            [0, 8, 7, 0, 0, 0, 0, 3, 1],
            [0, 0, 3, 0, 1, 0, 0, 8, 0],
            [9, 0, 0, 8, 6, 3, 0, 0, 5],
            [0, 5, 0, 0, 9, 0, 6, 0, 0],
            [1, 3, 0, 0, 0, 0, 2, 5, 0],
            [0, 0, 0, 0, 0, 0, 0, 7, 4],
            [0, 0, 5, 2, 0, 6, 3, 0, 0],
        ]

        solved_board = [
            [3, 1, 6, 5, 7, 8, 4, 9, 2],
            [5, 2, 9, 1, 3, 4, 7, 6, 8],
            [4, 8, 7, 6, 2, 9, 1, 3, 5],
            [2, 6, 3, 4, 1, 5, 9, 8, 7],
            [9, 7, 4, 8, 6, 3, 2, 1, 5],
            [8, 5, 1, 7, 9, 2, 6, 4, 3],
            [1, 3, 8, 9, 4, 7, 2, 5, 6],
            [6, 9, 2, 3, 5, 1, 8, 7, 4],
            [7, 4, 5, 2, 8, 6, 3, 1, 9],
        ]

        return (unsolved_board, solved_board)
