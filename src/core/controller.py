import logging
from abc import ABC, abstractmethod

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

class GameController:
    def __init__(self, engine, uimanager):
        logger.debug(">>>GameController::init - Initializing GameController")
        self._engine = engine
        self._uimanager = uimanager
        self._engine.set_controller(self)
        self._uimanager.set_controller(self)

        self._board = None
        self._solution = None
        self._moves_counter = 0 # Keep track of correct moves
        self._wrong_moves_counter = 0 # Keep track of mistakes
        self._is_game_over = False
        self._notes_mode = False
        self._counts = {i: 0 for i in range(1, 10)}  # Initialize counts for numbers 1-9

    def start_game(self, difficulty):
        """
        Start the game by generating a new Sudoku puzzle.
        """
        logger.info(f">GameController::start_game - Starting new game with difficulty: {difficulty}")
        self._board, self._solution = self._engine.generator.generate(difficulty)
        # Reset counters for the new game
        self._moves_counter = 0
        self._wrong_moves_counter = 0
        self._is_game_over = False
        self._notes_mode = False
        self._counts = {i: 0 for i in range(1, 10)} # Reset number counts

        # Pass the generated board to the UI manager to display
        self._uimanager.start_game(self._board)
        # Note: UIManager.start_game now handles resetting its own displays (timer, moves)

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
        logger.debug(f">>>GameController::accumulate_wrong_moves - Accumulating wrong moves: {value_to_accumulate}. Current total: {self._wrong_moves_counter + value_to_accumulate}")
        self._wrong_moves_counter += value_to_accumulate

        self._is_game_over = self._check_game_over()
        if self._is_game_over:
             logger.info(">GameController::accumulate_wrong_moves - Game over condition met.")
             # UIManager will handle the game over state visually based on is_game_over() check after move attempt

        return self._wrong_moves_counter
    
    def numbers_placed_on_board(self, board):
        """
        Count how many of each number are already placed on the board.
        
        Args:
            board: The current Sudoku board
            
        Returns:
            dict: A dictionary mapping numbers to their occurrence counts
        """
        self._counts = {i: 0 for i in range(1, 10)}  # Reset counts
        for row in range(9):
            for col in range(9):
                value = board[row][col]
                if value != 0:
                    self._counts[value] = self._counts.get(value, 0) + 1
        return self._counts

    def place_number(self, number):
        """
        Update the counts to be shown in the number panel. another number has been placed.
        Args:
            number: The number to be placed.        
        """
        return self.update_counts(number, +1)
    
    def unplace_number(self, number):
        """
        Update the counts to be shown in the number panel. another number has been unplaced.
        Args:
            number: The number to be unplaced.        
        """
        return self.update_counts(number, -1)
    
    def update_counts(self, number, value):
        """
        Update the counts to be shown in the number panel.
        Args:
            number: The number to be updated.
            value: The value to add or subtract from the count.
        """
        logger.debug(f">>>GameController::update_counts - Updating counts for number {number} by {value}")
        if number in self._counts:
            self._counts[number] += value
        else:
            self._counts[number] = value

        return self._counts
    
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
            Accumulate correct moves made by the player.
            Args:
                value_to_accumulate: The value to accumulate (should be 1 for a correct move).
            Returns:
                int: The updated correct moves counter.
        """
        if value_to_accumulate > 0: # Only count positive accumulations as moves
             logger.debug(f">>>GameController::accumulate_moves - Accumulating correct moves: {value_to_accumulate}. Current total: {self._moves_counter + value_to_accumulate}")
             self._moves_counter += value_to_accumulate
        elif value_to_accumulate < 0:
             logger.warning(f">>>GameController::accumulate_moves - Received negative value, ignoring: {value_to_accumulate}")
        # else: value is 0, do nothing

        # Check for win condition (optional, could be added here or in UIManager)
        # if self._is_board_complete_and_correct():
        #    logger.info("Board completed successfully!")
        #    # Trigger win state in UI

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

    def solve_puzzle(self):
        """
        Solve the Sudoku puzzle.
        
        Returns:
            list: The solved Sudoku board.
        """
        logger.debug(">>>GameController::solve_puzzle - Solving puzzle")
        return self._engine.solve(self._board)