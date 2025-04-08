from abc import ABC, abstractmethod
from typing import List
from core.controller import ControllerDependent
import logging

logger = logging.getLogger(__name__)


class GameEngine(ControllerDependent):
    def __init__(self, difficulty, generator, solver):
        logger.debug(">>>GameEngine::init - Initializing GameEngine")
        self.generator = generator
        self.solver = solver
        self.difficulty = difficulty

    def get_current_difficulty(self):
        """
        Get the current difficulty level.

        Returns:
            Difficulty: The current difficulty level.
        """
        return self.difficulty

    def set_controller(self, controller):
        """
        Set the controller for this GameEngine.

        Args:
            controller: The controller instance.
        """
        logger.debug(">>>GameEngine::set_controller - Setting controller")
        self.controller = controller

    def start_game(self):
        """
        Start the game by generating a new Sudoku puzzle.
        """
        logger.debug(">>>GameEngine::start_game - Starting new game")
        self._board, self._solution = self.generator.generate(self.difficulty)
        return self._board, self._solution


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
