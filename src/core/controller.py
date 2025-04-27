import logging
import time
import uuid
from abc import ABC, abstractmethod
from monitoring.metrics import get_metrics_service

logger = logging.getLogger(__name__)

# Define MAX_WRONG_MOVES here so it's accessible by ui_components
MAX_WRONG_MOVES = 3

class ControllerDependent(ABC):
    """
    Abstract base class for components that depend on a controller.
    
    Attributes:
        controller: The controller instance.
    """
    @abstractmethod
    def set_controller(self, controller):
        """
        Set the controller for this component.
        
        Args:
            controller: The controller instance.
        """
        pass

class TimerManager:
    """
    Manages game timing functionality.
    Single responsibility: Handle all timer-related operations.
    """
    def __init__(self):
        """Initialize the timer manager."""
        self._start_time = None
        self._is_running = False
        
    def start(self):
        """Start or restart the timer."""
        logger.debug("> TimerManager::start - Starting timer")
        self._start_time = time.time()
        self._is_running = True
        return self._start_time
        
    def stop(self):
        """Stop the timer."""
        logger.debug("> TimerManager::stop - Stopping timer")
        self._is_running = False
        
    def get_elapsed_time(self):
        """
        Get the elapsed time in seconds since the timer was started.
        
        Returns:
            int: Elapsed time in seconds, or 0 if timer isn't running
        """
        if not self._is_running or self._start_time is None:
            return 0
            
        return int(time.time() - self._start_time)
        
    def is_running(self):
        """
        Check if the timer is currently running.
        
        Returns:
            bool: True if the timer is running, False otherwise
        """
        return self._is_running
        
    def reset(self):
        """Reset the timer to initial state."""
        logger.debug("> TimerManager::reset - Resetting timer")
        self._start_time = None
        self._is_running = False

class NotesManager:
    """
    Manages notes functionality.
    Single responsibility: Handle all notes-related operations.
    """
    def __init__(self):
        """Initialize the notes manager."""
        self._notes_mode = False
        self._auto_notes_mode = False
        
    def toggle_notes_mode(self):
        """
        Toggle the notes mode on or off.
        
        Returns:
            bool: The new state of notes mode
        """
        logger.debug("> NotesManager::toggle_notes_mode - Toggling notes mode. Current state: %s", self._notes_mode)
        self._notes_mode = not self._notes_mode
        return self._notes_mode
        
    def toggle_auto_notes_mode(self):
        """
        Toggle the auto notes mode on or off.
        
        Returns:
            bool: The new state of auto notes mode
        """
        logger.debug("> NotesManager::toggle_auto_notes_mode - Toggling auto notes mode. Current state: %s", self._auto_notes_mode)
        self._auto_notes_mode = not self._auto_notes_mode
        return self._auto_notes_mode
        
    def get_notes_mode(self):
        """
        Get the current state of notes mode.
        
        Returns:
            bool: True if notes mode is enabled, False otherwise
        """
        return self._notes_mode
        
    def get_auto_notes_mode(self):
        """
        Get the current state of auto notes mode.
        
        Returns:
            bool: True if auto notes mode is enabled, False otherwise
        """
        return self._auto_notes_mode
        
    def reset(self):
        """Reset notes modes to initial state."""
        logger.debug("> NotesManager::reset - Resetting notes modes")
        self._notes_mode = False
        self._auto_notes_mode = False

class BoardManager:
    """
    Manages the game board state.
    Single responsibility: Handle all board-related operations.
    """
    def __init__(self, engine):
        """
        Initialize the board manager.
        
        Args:
            engine: The game engine to use for board operations
        """
        self._engine = engine
        self._board = None
        self._solution = None
        self._counts = {i: 0 for i in range(1, 10)}
        
    def generate_board(self, difficulty):
        """
        Generate a new board with the specified difficulty.
        
        Args:
            difficulty: The difficulty level
            
        Returns:
            tuple: (board, solution)
        """
        logger.debug("> BoardManager::generate_board - Generating new board with difficulty: %s", difficulty)
        self._board, self._solution = self._engine.generator.generate(difficulty)
        return self._board, self._solution
        
    def is_input_correct(self, row, col, value):
        """
        Check if the input is correct according to the solution.
        
        Args:
            row: The row index
            col: The column index
            value: The value to check
            
        Returns:
            bool: True if the input is correct, False otherwise
        """
        return self._engine.is_input_correct(self._solution, row, col, value)
        
    def can_input(self, row, col, value):
        """
        Check if the input is valid for the board (for notes mode).
        
        Args:
            row: The row index
            col: The column index
            value: The value to check
            
        Returns:
            bool: True if the input is valid, False otherwise
        """
        return self._engine.can_input(self._board, row, col, value)
        
    def set_value(self, row, col, value):
        """
        Set a value on the board.
        
        Args:
            row: The row index
            col: The column index
            value: The value to set
        """
        logger.debug("> BoardManager::set_value - Setting board value at (%d, %d): %d", row, col, value)
        self._board[row][col] = value
        
    def get_board(self):
        """
        Get the current board.
        
        Returns:
            list: The current board
        """
        return self._board
        
    def get_solution(self):
        """
        Get the solution for the current board.
        
        Returns:
            list: The solution
        """
        return self._solution
        
    def solve(self):
        """
        Solve the current board.
        
        Returns:
            list: The solved board
        """
        logger.debug("> BoardManager::solve - Solving current board")
        return self._engine.solve(self._board)
        
    def count_numbers(self, board):
        """
        Count the occurrences of each number on the board.
        
        Args:
            board: The board to count numbers in
            
        Returns:
            dict: A dictionary mapping numbers to their counts
        """
        self._counts = {i: 0 for i in range(1, 10)}
        for row in range(9):
            for col in range(9):
                value = board[row][col]
                if value != 0:
                    self._counts[value] = self._counts.get(value, 0) + 1
        return self._counts
        
    def update_count(self, number, delta):
        """
        Update the count for a specific number.
        
        Args:
            number: The number to update
            delta: The change in count (positive or negative)
            
        Returns:
            dict: The updated counts
        """
        logger.debug("> BoardManager::update_count - Updating count for number %d by %d", number, delta)
        if number in self._counts:
            self._counts[number] += delta
        else:
            self._counts[number] = delta
        return self._counts
        
    def get_counts(self):
        """
        Get the current counts of numbers on the board.
        
        Returns:
            dict: The current counts
        """
        return dict(self._counts)

class GameController:
    """
    Main controller for the Sudoku game.
    Coordinates the various managers and components to run the game.
    """
    def __init__(self, engine, uimanager):
        """
        Initialize the game controller.
        
        Args:
            engine: The game engine to use
            uimanager: The UI manager to use
        """
        logger.debug("> GameController::init - Initializing GameController")
        
        # Set up dependencies using composition
        self._engine = engine
        self._uimanager = uimanager
        self._board_manager = BoardManager(engine)
        self._timer_manager = TimerManager()
        self._notes_manager = NotesManager()
        
        # Set up controller dependencies
        self._engine.set_controller(self)
        self._uimanager.set_controller(self)
        
        # Game state variables
        self._moves_counter = 0
        self._wrong_moves_counter = 0
        self._is_game_over = False
        self._current_game_id = None

    def start_game(self, difficulty):
        """
        Start a new game with the specified difficulty.
        """
        logger.info(">> GameController::start_game - Starting new game with difficulty: %s", difficulty)
        
        # Reset game state
        self._moves_counter = 0
        self._wrong_moves_counter = 0
        self._is_game_over = False
        
        # Use composition to delegate to specialized managers
        self._notes_manager.reset()
        self._timer_manager.reset()
        
        # Generate new board
        board, _ = self._board_manager.generate_board(difficulty)
        
        # Create new game ID for metrics
        self._current_game_id = str(uuid.uuid4())
        
        # Record game start in metrics
        metrics = get_metrics_service()
        if metrics:
            metrics.record_game_start(self._current_game_id)
            
        # Update UI
        self._uimanager.start_game(board)

    def is_valid_input(self, row, col, value):
        """
        Check if the input is valid for the current game mode.
        
        Args:
            row: The row index
            col: The column index
            value: The value to check
            
        Returns:
            bool: True if the input is valid, False otherwise
        """
        logger.debug("> GameController::is_valid_input - Checking input at (%d, %d): %d", row, col, value)
        
        # Use notes manager to determine validation mode
        if self._notes_manager.get_notes_mode():
            return self._board_manager.can_input(row, col, value)
        else:
            return self._board_manager.is_input_correct(row, col, value)
    
    def accumulate_wrong_moves(self, value_to_accumulate):
        """
        Accumulate wrong moves.
        
        Args:
            value_to_accumulate: The number of wrong moves to add
            
        Returns:
            int: The new total of wrong moves
        """
        if value_to_accumulate < 0:
            logger.warning(">>> GameController::accumulate_wrong_moves - Received invalid negative value, ignoring: %d", value_to_accumulate)
            return self._wrong_moves_counter
        
        logger.debug("> GameController::accumulate_wrong_moves - Accumulating %d wrong moves. New total: %d", 
                    value_to_accumulate, self._wrong_moves_counter + value_to_accumulate)
        
        self._wrong_moves_counter += value_to_accumulate
        
        # Record wrong moves in metrics
        metrics = get_metrics_service()
        if metrics and value_to_accumulate > 0:
            for _ in range(value_to_accumulate):
                metrics.record_wrong_move()

        # Check for game over
        self._is_game_over = self._check_game_over()
        if self._is_game_over:
            logger.info(">> GameController::accumulate_wrong_moves - Game over condition met")
            # Record game exit for game over
            if metrics:
                metrics.record_game_exit(self._current_game_id)

        return self._wrong_moves_counter
    
    def numbers_placed_on_board(self, board):
        """
        Count how many of each number are already placed on the board.
        
        Args:
            board: The current Sudoku board
            
        Returns:
            dict: A dictionary mapping numbers to their occurrence counts
        """
        return self._board_manager.count_numbers(board)

    def place_number(self, number):
        """
        Update the counts to be shown in the number panel when a number is placed.
        
        Args:
            number: The number to be placed
            
        Returns:
            dict: The updated counts
        """
        return self._board_manager.update_count(number, +1)
    
    def unplace_number(self, number):
        """
        Update the counts to be shown in the number panel when a number is unplaced.
        
        Args:
            number: The number to be unplaced
            
        Returns:
            dict: The updated counts
        """
        return self._board_manager.update_count(number, -1)
    
    def update_counts(self, number, value):
        """
        Update the counts to be shown in the number panel.
        
        Args:
            number: The number to be updated
            value: The value to add or subtract from the count
            
        Returns:
            dict: The updated counts
        """
        return self._board_manager.update_count(number, value)
    
    def _check_game_over(self):
        """
        Check if the game is over based on the number of wrong moves.
        
        Returns:
            bool: True if the game is over, False otherwise
        """
        logger.debug("> GameController::_check_game_over - Checking game over condition")
        return self._wrong_moves_counter >= MAX_WRONG_MOVES
    
    def is_game_over(self):
        """
        Check if the game is over.
        
        Returns:
            bool: True if the game is over, False otherwise
        """
        return self._is_game_over
    
    def accumulate_moves(self, value_to_accumulate):
        """
        Accumulate correct moves made by the player.
        
        Args:
            value_to_accumulate: The value to accumulate (should be 1 for a correct move)
            
        Returns:
            int: The updated correct moves counter
        """
        if value_to_accumulate > 0:
            logger.debug("> GameController::accumulate_moves - Accumulating %d correct moves. New total: %d", 
                        value_to_accumulate, self._moves_counter + value_to_accumulate)
            
            self._moves_counter += value_to_accumulate
            
            # Record moves in metrics
            metrics = get_metrics_service()
            if metrics:
                for _ in range(value_to_accumulate):
                    metrics.record_move()
        elif value_to_accumulate < 0:
            logger.warning(">>> GameController::accumulate_moves - Received negative value, ignoring: %d", value_to_accumulate)

        return self._moves_counter
    
    def set_board_value(self, row, col, value):
        """
        Set the value of a cell in the board.
        
        Args:
            row: The row index
            col: The column index
            value: The value to set
        """
        self._board_manager.set_value(row, col, value)

    def solve_puzzle(self):
        """
        Solve the Sudoku puzzle.
        
        Returns:
            list: The solved Sudoku board
        """
        logger.info(">> GameController::solve_puzzle - Solving puzzle")
        return self._board_manager.solve()
    
    # Timer methods - delegate to TimerManager
    def start_timer(self):
        """Start or restart the game timer."""
        return self._timer_manager.start()
    
    def stop_timer(self):
        """Stop the game timer."""
        self._timer_manager.stop()
    
    def get_elapsed_time(self):
        """Get the elapsed time in seconds."""
        return self._timer_manager.get_elapsed_time()
    
    def is_timer_running(self):
        """Check if the timer is running."""
        return self._timer_manager.is_running()
    
    # Notes methods - delegate to NotesManager
    def toggle_notes_mode(self):
        """Toggle notes mode on/off."""
        return self._notes_manager.toggle_notes_mode()
    
    def toggle_auto_notes_mode(self):
        """Toggle auto notes mode on/off."""
        return self._notes_manager.toggle_auto_notes_mode()
    
    def get_notes_mode(self):
        """Get the current notes mode state."""
        return self._notes_manager.get_notes_mode()
    
    def get_auto_notes_mode(self):
        """Get the current auto notes mode state."""
        return self._notes_manager.get_auto_notes_mode()