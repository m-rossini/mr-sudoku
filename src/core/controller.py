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

class GameController:
    def __init__(self, engine, uimanager):
        logger.debug(">>>GameController::init - Initializing GameController")
        self._engine = engine
        self._uimanager = uimanager
        self._engine.set_controller(self)
        self._uimanager.set_controller(self)
        self._board = None
        self._solution = None

    def start_game(self):
        """
        Start the game by generating a new Sudoku puzzle.
        """
        logger.debug(">>>GameController::start_game - Starting new game")
        self._board, self._solution = self._engine.generator.generate(self._engine.get_current_difficulty())
        self._uimanager.start_game(self._board)
        return