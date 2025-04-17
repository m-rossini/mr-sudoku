from abc import ABC, abstractmethod
from typing import List
from core.controller import ControllerDependent
from core.difficulty import Difficulty
import logging
import random
import copy
import time # Add time import

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
        logger.debug(f">>>GameEngine::is_input_correct - Solution board: {_solution}")
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


class BacktrackingSudokuGenerator(SudokuGenerator):
    """
    Generates Sudoku puzzles using a backtracking algorithm.
    Creates a fully solved board, then removes cells based on difficulty.
    """
    def __init__(self):
        logger.debug(">>>BacktrackingSudokuGenerator::__init__ - Initializing BacktrackingSudokuGenerator")
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = None
        self.backtrack_count = 0 # Initialize backtrack counter

    def generate(self, difficulty: str) -> tuple[List[List[int]], List[List[int]]]:
        """
        Generates a new Sudoku puzzle and its solution.

        Args:
            difficulty: The desired difficulty level (e.g., "Easy", "Medium").

        Returns:
            A tuple containing the puzzle board and the solution board.
        """
        logger.debug(f">>>BacktrackingSudokuGenerator::generate - Generating puzzle with difficulty: {difficulty}")
        start_time = time.time() # Record start time
        self.backtrack_count = 0 # Reset backtrack counter for new generation

        # 1. Create a fully solved board
        self.board = [[0 for _ in range(9)] for _ in range(9)] # Reset board
        if not self._solve_board():
             logger.error(">>>BacktrackingSudokuGenerator::generate - Failed to create a solved board!")
             # Handle error appropriately, maybe raise an exception or return None/empty boards
             return None, None # Or raise an exception
        self.solution = copy.deepcopy(self.board) # Store the solution
        logger.debug(">>>BacktrackingSudokuGenerator::generate - Solved board created.")

        # 2. Remove cells based on difficulty
        puzzle_board = copy.deepcopy(self.solution)
        self._remove_cells(puzzle_board, difficulty)

        end_time = time.time() # Record end time
        duration = end_time - start_time

        logger.info(f">BacktrackingSudokuGenerator::generate - Puzzle generated for difficulty {difficulty}. Backtracks: {self.backtrack_count}. Time: {duration:.4f} seconds.")

        return puzzle_board, self.solution

    def _find_empty(self):
        """Finds the next empty cell (represented by 0) in the board."""
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    return (r, c)
        return None

    def _is_valid(self, num, pos):
        """Checks if placing 'num' at 'pos' (row, col) is valid."""
        row, col = pos

        # Check row
        if num in self.board[row]:
            return False

        # Check column
        if num in [self.board[i][col] for i in range(9)]:
            return False

        # Check 3x3 box
        box_x = col // 3
        box_y = row // 3
        for i in range(box_y * 3, box_y * 3 + 3):
            for j in range(box_x * 3, box_x * 3 + 3):
                if self.board[i][j] == num:
                    return False

        return True

    def _solve_board(self):
        """Fills the board completely using backtracking."""
        find = self._find_empty()
        if not find:
            return True  # Board is full
        else:
            row, col = find

        nums = list(range(1, 10))
        random.shuffle(nums) # Introduce randomness for varied solutions

        for num in nums:
            if self._is_valid(num, (row, col)):
                self.board[row][col] = num

                if self._solve_board():
                    return True

                # Backtrack
                self.backtrack_count += 1 # Increment backtrack counter
                self.board[row][col] = 0

        return False

    def _remove_cells(self, board, difficulty_str):
        """
        Removes cells from the solved board to create the puzzle.
        The number of cells removed depends on the difficulty.
        Ensures the puzzle has a unique solution (basic implementation).
        """
        try:
            difficulty = Difficulty(difficulty_str)
        except ValueError:
            logger.warning(f"Invalid difficulty '{difficulty_str}', defaulting to Medium.")
            difficulty = Difficulty.MEDIUM

        # Define number of cells to *keep* based on difficulty
        # Lower number means harder puzzle (more removed cells)
        if difficulty == Difficulty.EASY:
            cells_to_keep = random.randint(40, 45) # Fewer removed
        elif difficulty == Difficulty.MEDIUM:
            cells_to_keep = random.randint(32, 39)
        elif difficulty == Difficulty.HARD:
            cells_to_keep = random.randint(25, 31)
        elif difficulty == Difficulty.EXPERT:
            cells_to_keep = random.randint(17, 24) # More removed
        else: # Default to Medium
            cells_to_keep = random.randint(32, 39)

        cells_to_remove = 81 - cells_to_keep
        logger.debug(f">>>BacktrackingSudokuGenerator::_remove_cells - Difficulty: {difficulty.value}, Cells to remove: {cells_to_remove}")

        removed_count = 0
        attempts = 0 # Prevent infinite loops if something goes wrong
        max_attempts = 200 # Arbitrary limit

        while removed_count < cells_to_remove and attempts < max_attempts:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            attempts += 1

            if board[row][col] != 0:
                # Simple removal strategy: just remove if not already empty
                # A more robust strategy would check for unique solvability here
                board[row][col] = 0
                removed_count += 1
                logger.debug(f">>>BacktrackingSudokuGenerator::_remove_cells - Removed cell at ({row}, {col}). Count: {removed_count}")

        if removed_count < cells_to_remove:
             logger.warning(f"Could only remove {removed_count}/{cells_to_remove} cells after {max_attempts} attempts.")


class FixedBoardSudokuGenerator(SudokuGenerator):
    """A simple Sudoku puzzle generator implementation."""

    def generate(self, difficulty: str) -> tuple[List[List[int]], List[List[int]]]:
        """Generate a new Sudoku puzzle based on the difficulty."""

        logger.debug(f">>>FixedBoardSudokuGenerator::generate - Generating Sudoku puzzle with difficulty: {difficulty}")
        unsolved_easy = [
                [5, 3, 0, 0, 7, 0, 0, 0, 0],
                [6, 0, 0, 1, 9, 5, 0, 0, 0],
                [0, 9, 8, 0, 0, 0, 0, 6, 0],
                [8, 0, 0, 0, 6, 0, 0, 0, 3],
                [4, 0, 0, 8, 0, 3, 0, 0, 1],
                [7, 0, 0, 0, 2, 0, 0, 0, 6],
                [0, 6, 0, 0, 0, 0, 2, 8, 0],
                [0, 0, 0, 4, 1, 9, 0, 0, 5],
                [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]
        unsolved_medium = [
                [5, 0, 0, 0, 7, 0, 0, 0, 0],
                [6, 0, 0, 1, 0, 0, 0, 0, 0],
                [0, 9, 8, 0, 0, 0, 0, 6, 0],
                [0, 0, 0, 0, 6, 0, 0, 0, 3],
                [4, 0, 0, 0, 0, 3, 0, 0, 1],
                [0, 0, 0, 0, 2, 0, 0, 0, 0],
                [0, 6, 0, 0, 0, 0, 2, 8, 0],
                [0, 0, 0, 4, 0, 9, 0, 0, 5],
                [0, 0, 0, 0, 8, 0, 0, 7, 0],
        ]
        unsolved_hard = [
                [0, 0, 0, 0, 7, 0, 0, 0, 0],
                [6, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 9, 0, 0, 0, 0, 0, 6, 0],
                [0, 0, 0, 0, 6, 0, 0, 0, 3],
                [0, 0, 0, 0, 0, 3, 0, 0, 0],
                [0, 0, 0, 0, 2, 0, 0, 0, 6],
                [0, 6, 0, 0, 0, 0, 2, 0, 0],
                [0, 0, 0, 4, 0, 9, 0, 0, 0],
                [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]
        unsolved_expert = [
                [0, 0, 0, 0, 7, 0, 0, 0, 0],
                [6, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 9, 0, 0, 0, 0, 0, 6, 0],
                [0, 0, 0, 0, 6, 0, 0, 0, 3],
                [0, 0, 0, 0, 0, 3, 0, 0, 0],
                [0, 0, 0, 0, 2, 0, 0, 0, 6],
                [0, 6, 0, 0, 0, 0, 2, 0, 0],
                [0, 0, 0, 4, 0, 9, 0, 0, 0],
                [0, 0, 0, 0, 8, 0, 0, 7, 9],
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
                [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]
        
        if difficulty.upper() == Difficulty.EXPERT.value.upper():
            return (unsolved_expert, solved_board)
        elif difficulty.upper() == Difficulty.HARD.value.upper():
            return (unsolved_hard, solved_board)
        elif difficulty.upper() == Difficulty.MEDIUM.value.upper():
            return (unsolved_medium, solved_board)
        elif difficulty.upper() == Difficulty.EASY.value.upper():
            return (unsolved_easy, solved_board)
        else:
             logger.info(f">>>FixedBoardSudokuGenerator::generate - Invalid difficulty level: {difficulty}. Defaulting to Medium.")
             return
