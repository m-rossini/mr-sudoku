import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)
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

MAX_WRONG_MOVES = 3
class GameController:
    def __init__(self, engine, uimanager):
        logger.debug(">>>GameController::init - Initializing GameController")
        self._engine = engine
        self._uimanager = uimanager
        self._engine.set_controller(self)
        self._uimanager.set_controller(self)
        self._board = None
        self._solution = None
        self._moves_counter = 0
        self._wrong_moves_counter = 0
        self._is_game_over = False
        self._notes_mode = False

    def start_game(self):
        """
        Start the game by generating a new Sudoku puzzle.
        """
        logger.debug(">>>GameController::start_game - Starting new game")
        self._board, self._solution = self._engine.generator.generate(self._engine.get_current_difficulty())
        self._uimanager.start_game(self._board)
        return

    def is_valid_input(self, row, col, value):
        logger.debug(f">>>GameController::handle_key_input - Key input at ({row}, {col}): {value}")
        if self._notes_mode:
            return self._engine.can_input(self._board, row, col, value)
        else:
            return self._engine.is_input_correct(self._solution, row, col, value)
    
    def accumulate_wrong_moves(self, value_to_accumulate):
        if value_to_accumulate < 0:
            logger.debug(f">>>GameController::accumulate_wrong_moves - Accumulating wrong moves received invalid value and it will be ignored: {value_to_accumulate}")
            return self._wrong_moves_counter
        logger.debug(f">>>GameController::accumulate_wrong_moves - Accumulating wrong moves: {value_to_accumulate}")
        self._wrong_moves_counter += value_to_accumulate

        self._is_game_over = self._check_game_over()
        
        return self._wrong_moves_counter
    
    def _check_game_over(self):
        """
        Check if the game is over based on the number of wrong moves.
        
        Returns:
            bool: True if the game is over, False otherwise.
        """
        logger.debug(f">>>GameController::_check_game_over - Checking game over condition")
        if self._wrong_moves_counter >= MAX_WRONG_MOVES:
            self._is_game_over = True
            return True
        return False
    
    def is_game_over(self):
        """
        Check if the game is over.
        
        Returns:
            bool: True if the game is over, False otherwise.
        """
        logger.debug(f">>>GameController::is_game_over - Checking if game is over: {self._is_game_over}")
        return self._is_game_over
    
    def accumulate_moves(self,value_to_accumulate):
        """
            Accumulate moves made by the player. If passed a negative value, it will be subtracted from the moves counter.
            if passed a zero value, it will not change the moves counter and will return the current moves counter.
            Args:
                value_to_accumulate: The value to accumulate.
            Returns:
                int: The updated moves counter.
        """
        logger.debug(f">>>GameController::accumulate_moves - Accumulating moves: {value_to_accumulate}")
        self._moves_counter += value_to_accumulate
        return self._moves_counter
    
    def set_board_value(self, row, col, value):
        """
        Set the value of a cell in the board.
        
        Args:
            row: The row index.
            col: The column index.
            value: The value to set.
        """
        logger.debug(f">>>GameController::set_board_value - Setting board value at ({row}, {col}): {value}")
        self._board[row][col] = value