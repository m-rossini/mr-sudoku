from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from core.controller import ControllerDependent
from core.difficulty import Difficulty
import logging
import random
import copy
import time

logger = logging.getLogger(__name__)


class BoardValidator:
    """
    Handles validation of Sudoku board positions.
    Single responsibility: Determine if a move is valid according to Sudoku rules.
    """
    
    def is_valid_position(self, board: List[List[int]], row: int, col: int, num: int) -> bool:
        """
        Check if placing 'num' at position (row, col) is valid.
        
        Args:
            board: The Sudoku board
            row: Row index
            col: Column index
            num: Number to check
            
        Returns:
            bool: True if the position is valid, False otherwise
        """
        logger.debug("> BoardValidator::is_valid_position - Checking if %d is valid at (%d, %d)", num, row, col)
        
        # Check row
        if num in board[row]:
            return False

        # Check column
        if num in [board[i][col] for i in range(9)]:
            return False

        # Check 3x3 box
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if board[i][j] == num:
                    return False

        return True
    
    def can_place_number(self, board: List[List[int]], row: int, col: int, value: int) -> bool:
        """
        Check if a value can be input at the specified position.
        
        Args:
            board: The Sudoku board
            row: Row index
            col: Column index
            value: Value to check
            
        Returns:
            bool: True if the input is valid, False otherwise
        """
        logger.debug("> BoardValidator::can_place_number - Checking input validity at (%d, %d): %d", row, col, value)

        # Check if cell is empty
        if board[row][col] != 0:
            logger.debug("> BoardValidator::can_place_number - Cell at (%d, %d) is not empty", row, col)
            return False
            
        return self.is_valid_position(board, row, col, value)


class DifficultyManager:
    """
    Manages difficulty settings for Sudoku puzzles.
    Single responsibility: Translate difficulty levels to game parameters.
    """
    
    def get_cells_to_keep(self, difficulty: Difficulty) -> int:
        """
        Get the number of cells to keep based on difficulty level.
        
        Args:
            difficulty: The difficulty level
            
        Returns:
            int: Number of cells to keep (filled) in the puzzle
        """
        logger.debug("> DifficultyManager::get_cells_to_keep - Getting cells for difficulty: %s", difficulty.value)
        
        # Define number of cells to *keep* based on difficulty
        # Lower number means harder puzzle (more removed cells)
        if difficulty == Difficulty.EASY:
            return random.randint(40, 45)  # Fewer removed
        elif difficulty == Difficulty.MEDIUM:
            return random.randint(32, 39)
        elif difficulty == Difficulty.HARD:
            return random.randint(25, 31)
        elif difficulty == Difficulty.EXPERT:
            return random.randint(17, 24)  # More removed
        else:  # Default to Medium if something unexpected happens
            logger.warning(">>> DifficultyManager::get_cells_to_keep - Unknown difficulty, defaulting to Medium")
            return random.randint(32, 39)


class CellRemovalStrategy:
    """
    Strategy for removing cells from a solved Sudoku board.
    Single responsibility: Remove cells according to the specified difficulty.
    """
    
    def __init__(self, difficulty_manager: DifficultyManager):
        """
        Initialize the cell removal strategy.
        
        Args:
            difficulty_manager: Manager for difficulty settings
        """
        self.difficulty_manager = difficulty_manager
    
    def remove_cells(self, board: List[List[int]], difficulty_str: str) -> None:
        """
        Remove cells from the solved board to create the puzzle.
        
        Args:
            board: The fully solved board to remove cells from
            difficulty_str: The difficulty level as a string
        """
        logger.debug("> CellRemovalStrategy::remove_cells - Removing cells for difficulty: %s", difficulty_str)
        
        try:
            difficulty = Difficulty(difficulty_str)
        except ValueError:
            logger.warning(">>> CellRemovalStrategy::remove_cells - Invalid difficulty '%s', defaulting to Medium", difficulty_str)
            difficulty = Difficulty.MEDIUM

        cells_to_keep = self.difficulty_manager.get_cells_to_keep(difficulty)
        cells_to_remove = 81 - cells_to_keep
        
        logger.debug("> CellRemovalStrategy::remove_cells - Difficulty: %s, Cells to remove: %d", 
                     difficulty.value, cells_to_remove)

        removed_count = 0
        attempts = 0
        max_attempts = 200  # Prevent infinite loops

        while removed_count < cells_to_remove and attempts < max_attempts:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            attempts += 1

            if board[row][col] != 0:
                board[row][col] = 0
                removed_count += 1

        if removed_count < cells_to_remove:
            logger.warning(">>> CellRemovalStrategy::remove_cells - Could only remove %d/%d cells after %d attempts",
                         removed_count, cells_to_remove, max_attempts)


class GameEngine(ControllerDependent):
    def __init__(self, generator, solver):
        logger.debug("> GameEngine::init - Initializing GameEngine")
        self.generator = generator
        self.solver = solver
        self.board_validator = BoardValidator()

    def solve(self, board):
        """
        Solve the Sudoku puzzle.

        Args:
            board: The Sudoku board to be solved.

        Returns:
            List[List[int]]: The solved Sudoku board.
        """
        logger.debug("> GameEngine::solve - Solving the Sudoku puzzle")
        return self.solver.solve(board)
    
    def set_controller(self, controller):
        """
        Set the controller for this GameEngine.

        Args:
            controller: The controller instance.
        """
        logger.debug("> GameEngine::set_controller - Setting controller")
        self.controller = controller

    def start_game(self, difficulty):
        """
        Start the game by generating a new Sudoku puzzle.
        
        Args:
            difficulty: The difficulty level
            
        Returns:
            tuple: The puzzle board and solution
        """
        logger.debug("> GameEngine::start_game - Starting new game with difficulty: %s", difficulty)
        self._board, self._solution = self.generator.generate(difficulty)
        return self._board, self._solution

    def is_input_correct(self, solution, row, col, value):
        """
        Check if the input value is correct according to the solution.

        Args:
            solution: The solution board
            row: The row index
            col: The column index
            value: The value to be checked

        Returns:
            bool: True if the input is correct, False otherwise
        """
        logger.debug("> GameEngine::is_input_correct - Checking if %d is correct at (%d, %d)", value, row, col)
        return solution[row][col] == value

    def can_input(self, board, row, col, value):
        """
        Check if a value can be input at the specified position.

        Args:
            board: The current Sudoku board
            row: The row index
            col: The column index
            value: The value to be checked

        Returns:
            bool: True if the input is valid, False otherwise
        """
        logger.debug("> GameEngine::can_input - Checking if %d can be placed at (%d, %d)", value, row, col)
        return self.board_validator.can_place_number(board, row, col, value)


class SudokuSolver(ABC):
    """Abstract base class for Sudoku puzzle solvers."""

    @abstractmethod
    def solve(self, board: List[List[int]]) -> List[List[int]]:
        """Solve a Sudoku puzzle."""
        pass


class SimpleSudokuSolver(SudokuSolver):
    """A simple Sudoku solver implementation."""

    def solve(self, board: List[List[int]]) -> List[List[int]]:
        """Solve the Sudoku puzzle."""
        logger.debug("> SimpleSudokuSolver::solve - Starting to solve the Sudoku puzzle")
        return board


class SudokuGenerator(ABC):
    """Abstract base class for Sudoku puzzle generators."""

    @abstractmethod
    def generate(self, difficulty: str) -> Tuple[List[List[int]], List[List[int]]]:
        """Generate a new Sudoku puzzle based on the difficulty."""
        pass


class BacktrackingSudokuGenerator(SudokuGenerator):
    """
    Generates Sudoku puzzles using a backtracking algorithm.
    Creates a fully solved board, then removes cells based on difficulty.
    """
    def __init__(self):
        logger.debug("> BacktrackingSudokuGenerator::__init__ - Initializing generator")
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = None
        self.backtrack_count = 0
        self.board_validator = BoardValidator()
        self.difficulty_manager = DifficultyManager()
        self.cell_remover = CellRemovalStrategy(self.difficulty_manager)

    def generate(self, difficulty: str) -> Tuple[List[List[int]], List[List[int]]]:
        """
        Generates a new Sudoku puzzle and its solution.

        Args:
            difficulty: The desired difficulty level

        Returns:
            A tuple containing the puzzle board and the solution board
        """
        logger.debug("> BacktrackingSudokuGenerator::generate - Generating puzzle with difficulty: %s", difficulty)
        start_time = time.time()
        self.backtrack_count = 0

        # Create a fully solved board
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        if not self._solve_board():
            logger.error(">>>> BacktrackingSudokuGenerator::generate - Failed to create a solved board!")
            return None, None
        
        self.solution = copy.deepcopy(self.board)
        logger.debug("> BacktrackingSudokuGenerator::generate - Solved board created")

        # Remove cells based on difficulty
        puzzle_board = copy.deepcopy(self.solution)
        self.cell_remover.remove_cells(puzzle_board, difficulty)

        end_time = time.time()
        duration = end_time - start_time

        logger.info(">> BacktrackingSudokuGenerator::generate - Puzzle generated for difficulty %s. "
                  "Backtracks: %d. Time: %.4f seconds", 
                  difficulty, self.backtrack_count, duration)

        return puzzle_board, self.solution

    def _find_empty(self) -> Optional[Tuple[int, int]]:
        """Finds the next empty cell (represented by 0) in the board."""
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    return (r, c)
        return None

    def _solve_board(self) -> bool:
        """
        Fills the board completely using backtracking.
        
        Returns:
            bool: True if the board is successfully solved, False otherwise
        """
        find = self._find_empty()
        if not find:
            return True  # Board is full
        
        row, col = find
        nums = list(range(1, 10))
        random.shuffle(nums)  # Introduce randomness for varied solutions

        for num in nums:
            if self.board_validator.is_valid_position(self.board, row, col, num):
                self.board[row][col] = num

                if self._solve_board():
                    return True

                # Backtrack
                self.backtrack_count += 1
                self.board[row][col] = 0

        return False


class FixedBoardSudokuGenerator(SudokuGenerator):
    """A simple Sudoku puzzle generator with predefined boards."""

    def __init__(self):
        """Initialize the fixed board generator."""
        logger.debug("> FixedBoardSudokuGenerator::__init__ - Initializing generator")
        self._prepare_boards()
        
    def _prepare_boards(self) -> None:
        """Prepare the predefined boards for each difficulty level."""
        logger.debug("> FixedBoardSudokuGenerator::_prepare_boards - Preparing predefined boards")
        
        # Solved board (the solution for all difficulties)
        self.solved_board = [
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
        
        # Different difficulty boards with varying number of empty cells
        self.difficulty_boards = {
            Difficulty.EASY.value: [
                [5, 3, 0, 0, 7, 0, 0, 0, 0],
                [6, 0, 0, 1, 9, 5, 0, 0, 0],
                [0, 9, 8, 0, 0, 0, 0, 6, 0],
                [8, 0, 0, 0, 6, 0, 0, 0, 3],
                [4, 0, 0, 8, 0, 3, 0, 0, 1],
                [7, 0, 0, 0, 2, 0, 0, 0, 6],
                [0, 6, 0, 0, 0, 0, 2, 8, 0],
                [0, 0, 0, 4, 1, 9, 0, 0, 5],
                [0, 0, 0, 0, 8, 0, 0, 7, 9],
            ],
            Difficulty.MEDIUM.value: [
                [5, 0, 0, 0, 7, 0, 0, 0, 0],
                [6, 0, 0, 1, 0, 0, 0, 0, 0],
                [0, 9, 8, 0, 0, 0, 0, 6, 0],
                [0, 0, 0, 0, 6, 0, 0, 0, 3],
                [4, 0, 0, 0, 0, 3, 0, 0, 1],
                [0, 0, 0, 0, 2, 0, 0, 0, 0],
                [0, 6, 0, 0, 0, 0, 2, 8, 0],
                [0, 0, 0, 4, 0, 9, 0, 0, 5],
                [0, 0, 0, 0, 8, 0, 0, 7, 0],
            ],
            Difficulty.HARD.value: [
                [0, 0, 0, 0, 7, 0, 0, 0, 0],
                [6, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 9, 0, 0, 0, 0, 0, 6, 0],
                [0, 0, 0, 0, 6, 0, 0, 0, 3],
                [0, 0, 0, 0, 0, 3, 0, 0, 0],
                [0, 0, 0, 0, 2, 0, 0, 0, 6],
                [0, 6, 0, 0, 0, 0, 2, 0, 0],
                [0, 0, 0, 4, 0, 9, 0, 0, 0],
                [0, 0, 0, 0, 8, 0, 0, 7, 9],
            ],
            Difficulty.EXPERT.value: [
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
        }

    def generate(self, difficulty: str) -> Tuple[List[List[int]], List[List[int]]]:
        """
        Generate a new Sudoku puzzle based on the difficulty.
        
        Args:
            difficulty: The difficulty level string
            
        Returns:
            A tuple containing the puzzle board and the solution board
        """
        logger.debug("> FixedBoardSudokuGenerator::generate - Generating puzzle with difficulty: %s", difficulty)
        
        try:
            difficulty_key = difficulty.upper()
            # Check if difficulty is valid
            if difficulty_key not in [d.value.upper() for d in Difficulty]:
                logger.warning(">>> FixedBoardSudokuGenerator::generate - Invalid difficulty: %s, defaulting to Medium", difficulty)
                difficulty_key = Difficulty.MEDIUM.value.upper()
                
            # Return deep copies to avoid modifying the original boards
            board = copy.deepcopy(self.difficulty_boards[difficulty_key])
            solution = copy.deepcopy(self.solved_board)
            
            return board, solution
            
        except Exception as e:
            logger.error(">>>> FixedBoardSudokuGenerator::generate - Error generating puzzle: %s", str(e))
            # Return default medium difficulty as fallback
            return (copy.deepcopy(self.difficulty_boards[Difficulty.MEDIUM.value]), 
                   copy.deepcopy(self.solved_board))
