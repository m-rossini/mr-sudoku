"""
Mr. Sudoku - Main entry point (Tkinter version)
"""

import sys
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import argparse
import logging
import uuid

# Add the parent directory to sys.path if running as script
if __name__ == "__main__":
    parent_dir = Path(__file__).resolve().parent.parent
    if parent_dir not in sys.path:
        sys.path.insert(0, str(parent_dir))

from core.ui_components import UIManager
from core.game import BacktrackingSudokuGenerator, SimpleSudokuSolver, GameEngine
from core.controller import GameController
from monitoring.metrics import initialize_metrics, get_metrics_service

# Configure logging
logger = logging.getLogger(__name__)

# Global game ID for metrics tracking
GAME_SESSION_ID = str(uuid.uuid4())


def setup_logging(log_level):
    """
    Configure logging with the specified log level.
    
    Args:
        log_level: The logging level to set
    """
    logging.basicConfig(
        level=log_level, 
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    logging.getLogger().setLevel(log_level)
    logger.info("> Main::setup_logging - Setting log level to %s", log_level)


def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    logger.debug("> Main::parse_arguments - Parsing command-line arguments")
    parser = argparse.ArgumentParser(description="Mr. Sudoku - Tkinter version")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)",
    )
    parser.add_argument(
        "--metrics-port",
        type=int,
        default=8000,
        help="Port for Prometheus metrics (default: 8000)",
    )
    return parser.parse_args()


def setup_metrics(port):
    """
    Initialize Prometheus metrics.
    
    Args:
        port: The port to expose metrics on
        
    Returns:
        bool: True if metrics were successfully initialized, False otherwise
    """
    try:
        logger.info("> Main::setup_metrics - Initializing Prometheus metrics on port %s", port)
        initialize_metrics(port)
        metrics = get_metrics_service()
        if metrics:
            metrics.record_game_start(GAME_SESSION_ID)
        return True
    except Exception as e:
        logger.warning(">> Main::setup_metrics - Failed to initialize metrics: %s", e)
        return False


def create_ui():
    """
    Create the main UI window.
    
    Returns:
        tk.Tk: The root window
    """
    logger.debug("> Main::create_ui - Creating main UI window")
    root = tk.Tk()
    root.title("Mr. Sudoku")
    return root


def setup_game_components(root):
    """
    Initialize game components (engine, UI manager, controller).
    
    Args:
        root: The root window
        
    Returns:
        GameController: The initialized game controller
    """
    logger.debug("> Main::setup_game_components - Initializing game components")
    
    # Create game engine components
    generator = BacktrackingSudokuGenerator()
    solver = SimpleSudokuSolver()
    engine = GameEngine(generator, solver)
    
    # Create UI manager and controller
    uimanager = UIManager(root, on_closing)  # Pass on_closing as a dependency
    controller = GameController(engine, uimanager)
    
    # Start the initial game
    controller.start_game(uimanager.get_difficulty())
    return controller


def on_closing(root):
    """
    Handle window close event by asking for confirmation.

    Args:
        root: The root window
    """
    logger.debug("> Main::on_closing - User attempted to close the game")

    if messagebox.askyesno("Quit", "Are you sure you want to quit the game?"):
        logger.info(">> Main::on_closing - User confirmed exit. Closing game.")
        
        # Record game exit in metrics
        metrics = get_metrics_service()
        if metrics:
            metrics.record_game_exit(GAME_SESSION_ID)
            
        # Perform any cleanup needed here (save game state, etc.)
        root.destroy()
    else:
        logger.debug("> Main::on_closing - User canceled exit")


def run_main_loop(root):
    """
    Run the main application loop.
    
    Args:
        root: The root window
        controller: The game controller
        
    Returns:
        int: Exit code (0 for success)
    """
    try:
        logger.debug("> Main::run_main_loop - Starting Tkinter event loop")
        root.mainloop()
        logger.debug("> Main::run_main_loop - Tkinter event loop ended")
        
        # Record game exit in metrics
        metrics = get_metrics_service()
        if metrics:
            metrics.record_game_exit(GAME_SESSION_ID)
            
        return 0
    except Exception as e:
        logger.error(">>>> Main::run_main_loop - Error in main loop: %s", str(e), exc_info=True)
        return 1


def main():
    """
    Main entry point for the Sudoku game, orchestrating the application flow.
    """
    try:
        # Parse arguments and setup logging
        args = parse_arguments()
        setup_logging(args.log_level)
        
        # Initialize metrics
        setup_metrics(args.metrics_port)
        
        # Create and configure UI
        root = create_ui()
        root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
        
        # Initialize game components
        controller = setup_game_components(root)
        
        # Run main application loop
        return run_main_loop(root)
    except Exception as e:
        logger.critical(">>>> Main::main - Critical error starting game: %s", str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
