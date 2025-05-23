import tkinter as tk
import logging
from core.controller import ControllerDependent
import time
from core.difficulty import Difficulty
from tkinter import messagebox
from core.controller import MAX_WRONG_MOVES
from monitoring.metrics import get_metrics_service

logger = logging.getLogger(__name__)


class UIManager(ControllerDependent):
    FLASH_DURATION_MS = 200
    SOLVE_REQUEST_EVENT = "<<SolveRequest>>"
    NEW_GAME_REQUEST_EVENT = "<<NewGameRequest>>"
    EXIT_GAME_REQUEST_EVENT = "<<ExitGameRequest>>"
    NOTES_MODE_REQUEST_EVENT = "<<NotesModeRequest>>"
    AUTO_NOTES_MODE_REQUEST_EVENT = "<<AutoNotesModeRequest>>"

    def __init__(self, root, on_closing):
        """
        Initialize the UIManager.

        Args:
            root: The root Tkinter window.
            on_closing: The function to handle the window close event.
        """
        logger.debug(">>>UIManager::init - Initializing UIManager")
        self.root = root
        self.on_closing = on_closing  # Store the on_closing function

        # Main frame for all components
        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.container_frame = tk.Frame(self.main_frame)
        self.board_frame = tk.Frame(self.container_frame)
        self.control_frame = tk.Frame(self.container_frame)

        self.board = self._create_board(self.board_frame)
        self.number_panel = self._create_number_panel()
        self.info_panel = self._create_info_panel(self.board_frame)
        self.difficulty_selector = self._create_difficulty_selector(self.control_frame)
        self.options_panel = self._create_options_panel(self.control_frame)
        self.button_panel = self._create_button_panel(self.control_frame, )
        self._layout_frames()
        self._create_top_level_bindings()

    def start_game(self, board):
        """
        Start a new game by displaying the Sudoku board.

        Args:
            board: The Sudoku board to display.
        """
        logger.debug("--------------------------------------------------------------------")
        logger.debug("> UIManager::start_game - Starting a new game")
        
        try:
            # Reset board properly - we need to both destroy widgets AND reset our tile references
            # First, remove all widgets from the board frame
            for widget in self.board.frame.winfo_children():
                widget.destroy()
                
            # Reset the board's internal state to ensure it creates a new board
            self.board.reset_board()
            
            # Now update with new values which will trigger board creation
            self.board.update_board_values(board)
            
            # Ensure the board is properly placed in the layout
            self.board.frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")
            
            # Update game state
            counts = self.controller.numbers_placed_on_board(board)
            self.number_panel.update_all_numbers(counts)
            self.number_panel.enable_all()
            self.info_panel.reset()
            self._start_timer()
            self.info_panel.update_wrong_moves(self.controller._wrong_moves_counter)
            self.info_panel.update_moves(self.controller._moves_counter)
        except Exception as e:
            logger.error(">>>> UIManager::start_game - Error starting game: %s", str(e))
            messagebox.showerror("Error", f"Failed to start new game: {str(e)}")

    def _create_options_panel(self, parent):
        """
        Create the options panel for additional game settings.

        Args:
            parent: The parent widget.

        Returns:
            OptionsPanel: The created options panel.
        """
        logger.debug(">>>UIManager::_create_options_panel - Creating OptionsPanel")
        options_panel = OptionsPanel(parent)
        return options_panel

    def _create_difficulty_selector(self, parent):
        """
        Create the difficulty selector.

        Args:
            parent: The parent widget.

        Returns:
            DifficultySelector: The created difficulty selector.
        """
        logger.debug(">>>UIManager::_create_difficulty_selector - Creating DifficultySelector")
        difficulty_selector = DifficultySelector(self.control_frame, on_difficulty_change=self._on_difficulty_change)
        return difficulty_selector

    def _create_info_panel(self, parent):
        """
        Create the info panel for displaying game information.

        Args:
            parent: The parent widget.

        Returns:
            InfoPanel: The created info panel.
        """
        logger.debug(">>>UIManager::_create_info_panel - Creating InfoPanel")
        infopanel = InfoPanel(self.board_frame)
        return infopanel

    def _layout_frames(self):
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        self.container_frame.pack(expand=True, fill=tk.BOTH)
        self.board_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH)
        self.board_frame.columnconfigure(0, weight=1)  # Single column
        self.board.frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.info_panel.frame.grid(row=2, column=0, pady=(0, 5), sticky="ew")
        self.spacer_frame = tk.Frame(self.board_frame)
        self.spacer_frame.grid(row=3, column=0, sticky="news")
        self.board_frame.rowconfigure(3, weight=1)  # Make spacer expandable
        self.control_spacer = tk.Frame(self.control_frame)
        self.control_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH)
        self.difficulty_selector.frame.pack(side=tk.TOP, pady=10)
        self.options_panel._frame.pack(side=tk.TOP, pady=10)
        self.button_panel.frame.pack(side=tk.TOP, pady=10)
        self.control_spacer.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def _create_top_level_bindings(self):
        self.root.bind(UIManager.NOTES_MODE_REQUEST_EVENT, lambda e: self._on_notes_mode(e))
        self.root.bind(UIManager.AUTO_NOTES_MODE_REQUEST_EVENT, lambda e: self._on_auto_notes_mode(e))

        self.root.bind("<Key>", self._on_key_press)

    def _create_number_panel(self):
        """
        Create the number panel for displaying number counts.
        """
        number_panel = NumberPanel(self.board_frame, self._on_number_click)
        number_panel.frame.grid(row=1, column=0, pady=5, sticky="ew")
        return number_panel

    def _create_board(self, parent):
        """
        Create the Sudoku board.

        Args:
            parent: The parent widget.

        Returns:
            SudokuBoard: The created Sudoku board.
        """
        logger.debug(">>>UIManager::_create_board - Creating Sudoku board")
        empty_board = [[0 for _ in range(9)] for _ in range(9)]
        return SudokuBoard(parent, empty_board, on_tile_click=self._on_tile_click)

    def _create_button_panel(self, parent):
        """
        Create the button panel.

        Args:
            parent: The parent widget.

        Returns:
            ButtonPanel: The created button panel.
        """
        logger.debug(">>>UIManager::_create_button_panel - Creating button panel")
        button_panel = ButtonPanel(self.control_frame, )
        button_panel.solve_button.bind(UIManager.SOLVE_REQUEST_EVENT, lambda e: self._on_solve())
        button_panel.new_game_button.bind(UIManager.NEW_GAME_REQUEST_EVENT, lambda e: self._on_new_game())
        button_panel.exit_button.bind(UIManager.EXIT_GAME_REQUEST_EVENT, lambda e: self._on_exit())
        return button_panel

    def _adjust_number_panel_width(self):
        """
        Adjust the number panel width to exactly match the board width.
        """
        # Get the *exact* board width without padding
        board_width = self.board.frame.winfo_width()
        self.number_panel.set_width(board_width)
        number_panel_width = self.number_panel.frame.winfo_width()

        if number_panel_width != board_width:
            self.number_panel.frame.config(width=board_width)

    def set_controller(self, controller):
        """
        Set the controller for this UIManager.

        Args:
            controller: The controller instance.
        """
        logger.debug(">>>UIManager::set_controller - Setting controller")
        self.controller = controller

    #the virtual event has data attached
    def _on_auto_notes_mode(self):
        """
        Handle the auto notes mode event.
        """
        self.controller.toggle_auto_notes_mode()

    def _on_notes_mode(self,):
        self.controller.toggle_notes_mode()

    def on_game_over(self):
        logger.debug(">>>UIManager::on_game_over - Game over")
        self._stop_timer()  # Stop the timer
        time.sleep(UIManager.FLASH_DURATION_MS / 1000)
        self.board.disable_board()
        self.number_panel.disable_all()

        logger.info(">UIManager::on_game_over - Game Over! You have made too many wrong moves!")
        messagebox.showinfo("Game Over", "Game Over! You have made too many mistakes.")

    def _on_tile_click(self, row, col):
        """Handle tile click events."""
        logger.debug(f">>>UIManager::_on_tile_click - Tile clicked at position ({row}, {col})")

    def _on_key_press(self, event):
        """
        Handle key press events.

        Args:
            event: The key event object
        """
        logger.debug(f">>>UIManager::_on_key_press - Key pressed: {event.keysym}, char: {event.char}")

        # Get the currently selected cell, if any
        selected_pos = self.board.get_selected_position()
        if not selected_pos:
            logger.info(">>>UIManager::_on_key_press - No cell selected, ignoring key press")
            return

        row, col = selected_pos
        if self.board.tiles[row][col].is_fixed:
            return

        if event.char.isdigit() and "1" <= event.char <= "9":
            value = int(event.char)
            is_valid = self._handle_number_input(row, col, value)
            if is_valid:
                counts = self.controller.place_number(value)
                self.number_panel.update_number_count(value, counts[value])
            else:
                if self.controller.is_game_over():
                    logger.info(">>>UIManager::_on_key_press - Game over due to too many wrong moves")
                    self.on_game_over()
        elif event.keysym in ("BackSpace", "Delete"):
            value = self.board.tiles[row][col].value
            if self.board.tiles[row][col].is_correct_value():
                logger.debug(f">>>UIManager::_on_key_press - Deleting value {value} at ({row}, {col})")
                counts = self.controller.unplace_number(value)
                self.number_panel.update_number_count(value, counts[value])

            self._handle_delete_input(row, col)

        else:
            logger.info(f">UIManager::_on_key_press - Not supported key: {event.keysym}")

    def _handle_number_input(self, row, col, value):
        """
        Handle number input for the selected cell.
        Args:
            row: Row index of the selected cell
            col: Column index of the selected cell
            value: The numeric value to input (1-9)

        Returns:
            bool: True if the input was valid, False otherwise.
        """
        logger.debug(f">>>UIManager::_handle_number_input - Inputting value {value} at ({row}, {col})")

        # Check if the input is valid
        is_valid = self.controller.is_valid_input(row, col, value)
        if is_valid:
            logger.debug(f">>>UIManager::_handle_number_input - Valid input: {value}")
            self.board.tiles[row][col].set_value(value)
            self.controller.set_board_value(row, col, value)
            correct_moves = self.controller.accumulate_moves(1)
            self.info_panel.update_moves(correct_moves)  # Update moves display
        else:
            logger.warning(f">UIManager::_handle_number_input - Invalid input: {value}")
            # Use the class constant for flash duration
            self.board.tiles[row][col].set_wrong_value(value)
            # Don't set the board value for wrong moves if you want them temporary
            # self.controller.set_board_value(row, col, value) # Optional: Decide if wrong moves persist
            wrong_moves = self.controller.accumulate_wrong_moves(1)
            self.info_panel.update_wrong_moves(wrong_moves)  # Update wrong moves display

        return is_valid

    def _handle_delete_input(self, row, col):
        """
        Handle delete input for the selected cell.

        Args:
            row: Row index of the selected cell
            col: Column index of the selected cell
        """
        logger.debug(f">>>UIManager::_handle_delete_input - Deleting value at ({row}, {col})")
        self.board.clear_highlights()
        self.board.tiles[row][col].set_value(0)
        self.controller.set_board_value(row, col, 0)

    def _on_new_game(self):
        """
        Handle the "New Game" button click with robust error handling.
        """
        logger.info(">> UIManager::_on_new_game - Starting a new game")
        try:
            # Stop the timer before starting a new game
            self._stop_timer()
            
            # Get current difficulty
            difficulty = self.difficulty_selector.get_difficulty()
            logger.debug("> UIManager::_on_new_game - Using difficulty: %s", difficulty)
            
            # Start a new game with the selected difficulty
            self.controller.start_game(difficulty)
        except Exception as e:
            logger.error(">>>> UIManager::_on_new_game - Error starting new game: %s", str(e))
            messagebox.showerror("Error", f"Failed to start new game: {str(e)}")

    def _on_solve(self):
        """
        Handle the "Solve" button click.
        """
        logger.info(">UIManager::_on_solve - Solving the puzzle")
        self.controller.solve_puzzle()

    def _on_exit(self):
        """
        Handle the "Exit" button click.
        """
        logger.info(">UIManager::_on_exit - Exiting the game")
        self._stop_timer()  # Stop timer before potentially closing
        self.on_closing(self.root)  # Call the on_closing function

    def get_difficulty(self):
        """
        Get the currently selected difficulty level from the difficulty selector.

        Returns:
            str: The selected difficulty level.
        """
        return self.difficulty_selector.get_difficulty()

    def _on_difficulty_change(self, difficulty):
        """
        Handle difficulty change events.

        Args:
            difficulty: The new difficulty level selected.
        """
        logger.info(f">UIManager::_on_difficulty_change - Difficulty changed to {difficulty}")
        # Ask the user in a message box if they want to start a new game since it changed the difficulty level

        if messagebox.askyesno(
                "Change Difficulty",
                "Changing difficulty will start a new game. Do you want to continue?",
        ):
            self._stop_timer()  # Stop timer for the old game
            self.difficulty_selector._set_difficulty(Difficulty(difficulty))
            self.controller.start_game(self.get_difficulty())
        else:
            logger.debug(f">>>UIManager::_on_difficulty_change - Not changing difficulty to: {difficulty}")
            self.difficulty_selector.reset_difficulty()

    def _on_number_click(self, number):
        """
        Handle number button click events from the NumberPanel.

        Args:
            number: The number clicked.
        """
        logger.debug(f">>>UIManager::_on_number_click - Number {number} clicked")
        # Simulate a key press for the selected number
        selected_pos = self.board.get_selected_position()
        if selected_pos:
            row, col = selected_pos
            self._handle_number_input(row, col, number)
        else:
            logger.info(">UIManager::_on_number_click - No cell selected, ignoring number click")

    # --- Timer Methods ---
    def _start_timer(self):
        """Starts the game timer."""
        if not self.controller.is_timer_running():
            # Let the controller start/track the actual timer
            self.controller.start_timer()
            self._timer_running = True
            self._update_timer_display()  # Start the update loop

    def _stop_timer(self):
        """Stops the game timer."""
        logger.debug("> UIManager::_stop_timer - Stopping game timer")
        
        # Check if the timer exists using direct attribute access
        if hasattr(self, '_timer_running') and getattr(self, '_timer_running', False):
            self._timer_running = False
            # Tell the controller to stop its timer
            self.controller.stop_timer()
            
            # Cancel any pending timer updates
            if hasattr(self, '_timer_id') and self._timer_id:
                self.root.after_cancel(self._timer_id)
                self._timer_id = None

    def is_timer_running(self):
        """
        Check if the timer is currently running.
        
        Returns:
            bool: True if the timer is running, False otherwise
        """
        logger.debug("> UIManager::is_timer_running - Checking if timer is running")
        # Use the controller to check the timer status
        return hasattr(self, '_timer_running') and self._timer_running

    def _update_timer_display(self):
        """Updates the timer label every second."""
        if self.controller.is_timer_running():
            # Get the elapsed time from the controller
            elapsed_seconds = self.controller.get_elapsed_time()
            minutes = elapsed_seconds // 60
            seconds = elapsed_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            self.info_panel.update_time(time_str)
            # Schedule the next update
            self._timer_id = self.root.after(1000, self._update_timer_display)
        elif self._timer_running:
            # Controller timer is stopped but UI thinks it's running
            self._timer_running = False


class SudokuTile:
    """A single tile/cell in the Sudoku grid."""

    def __init__(self, parent, row, col, value, on_click=None):
        """
        Initialize a new Sudoku tile.

        Args:
            parent: Parent widget
            row: Row index of this tile (0-8)
            col: Column index of this tile (0-8)
            value: The initial value of the tile (0 for empty)
            on_click: Callback function when tile is clicked
        """
        self.row = row
        self.col = col
        self.on_click = on_click
        self.value = value
        self.is_fixed = value != 0
        self.is_selected = False
        self._is_wrong = False

        # Create the tile frame
        self.frame = tk.Frame(parent, width=50, height=50, borderwidth=1, relief=tk.RAISED)

        self.frame.grid_propagate(False)

        # Create the tile label for displaying the value
        self.label = tk.Label(
            self.frame,
            text="",
            font=("Arial", 18, "bold"),
            width=2,
            height=1,
            bg="white",
        )
        self.label.pack(expand=True, fill=tk.BOTH)
        self.set_value(value)

        # Bind click events
        self.label.bind("<Button-1>", self._handle_click)
        self.frame.bind("<Button-1>", self._handle_click)

    def _handle_click(self, event):
        """Handle click events on the tile."""
        logger.debug(f">>>SudokuTile::_handle_click - Tile ({self.row}, {self.col}) clicked")
        if self.on_click:
            self.on_click(self.row, self.col)

    def set_value(self, value):
        """
        Set the tile's value and update its appearance.

        Args:
            value: The numeric value (0 for empty)
        """
        self.value = value
        self._is_wrong = False

        # Update the display text
        if value == 0:
            self.label.config(text="")
        else:
            self.label.config(text=str(value))

        if self.is_fixed:
            self.label.config(fg="black", bg="#f0f0f0")
        else:
            self.label.config(fg="black", bg="white")

    def set_wrong_value(self, value):
        """
        Set the tile's value to a wrong value and update its appearance.

        Args:
            value: The numeric value (0 for empty)
        """
        self.value = value
        self._is_wrong = True
        self.label.config(text=str(value))
        self.flash(color="red", duration=UIManager.FLASH_DURATION_MS)
        self.label.config(fg="red", bg="white")

    def is_correct_value(self):
        return not self._is_wrong

    def select(self, selected=True):
        """
        Select or deselect this tile.

        Args:
            selected: Whether the tile should be selected
        """
        self.is_selected = selected
        if selected:
            # Light blue background for selected tile
            self.label.config(bg="#c5e1e8")
        else:
            if self.is_fixed:
                self.label.config(bg="#f0f0f0")
            else:
                self.label.config(bg="white")

    def highlight(self, highlight=True, color="#e1f5fe"):
        """
        Highlight this tile (e.g., for matching values).

        Args:
            highlight: Whether to highlight the tile
            color: The color to use for highlighting (default: light blue)
        """
        # Don't highlight if already selected
        if self.is_selected:
            return

        if highlight:
            # Highlighted tiles have the specified background color
            self.label.config(bg=color)
        else:
            if self.is_fixed:
                self.label.config(bg="#f0f0f0")  # Light gray for fixed values
            else:
                self.label.config(bg="white")  # White for regular cells

    def flash(self, color="red", duration=UIManager.FLASH_DURATION_MS):
        """
        Flash the tile with a color temporarily.

        Args:
            color: Color to flash
            duration: Duration of flash in milliseconds
        """
        original_bg = self.label.cget("bg")
        self.label.config(bg=color)
        logger.debug(f">>>SudokuTile::flash - Flashing tile ({self.row}, {self.col}) with {color}")
        self.label.after(duration, lambda: self.label.config(bg=original_bg))


class SudokuBoard:
    """The 9x9 Sudoku game board."""

    def __init__(self, parent, board, on_tile_click=None):
        """
        Initialize a new Sudoku board.

        Args:
            parent: Parent widget
            on_tile_click: Callback function when a tile is clicked
        """
        logger.debug(">>>SudokuBoard::__init__ - Creating Sudoku board")
        self.parent = parent
        self.on_tile_click = on_tile_click

        # Create main frame
        self.frame = tk.Frame(parent)

        # Initialize tiles grid
        self.tiles = [[None for _ in range(9)] for _ in range(9)]

        # Currently selected tile position
        self.selected_pos = None
        # self._create_board(board)

    def _create_board(self, board):
        """Create the 9x9 Sudoku board with 3x3 boxes."""
        # Create the 3x3 boxes
        for box_row in range(3):
            for box_col in range(3):
                # Create a box with a thicker border
                box = tk.Frame(self.frame, borderwidth=2, relief=tk.RAISED)
                box.grid(row=box_row, column=box_col, padx=1, pady=1)

                # Create the 3x3 tiles within each box
                for cell_row in range(3):
                    for cell_col in range(3):
                        # Calculate global row and column
                        row = box_row * 3 + cell_row
                        col = box_col * 3 + cell_col

                        # Create the tile
                        tile = SudokuTile(
                            box,
                            row,
                            col,
                            value=board[row][col],
                            on_click=self._handle_tile_click,
                        )
                        tile.frame.grid(row=cell_row, column=cell_col)
                        # Store reference to the tile
                        self.tiles[row][col] = tile

        logger.debug(">>>SudokuBoard::_create_board - Board created with 9x9 grid")

    def update_board_values(self, board):
        """
        Update the board with new values. Creates the board if it doesn't exist yet.

        Args:
            board: The new Sudoku board values
        """
        logger.debug("> SudokuBoard::update_board_values - Updating board values")
        
        # Check if we need to create the board from scratch
        if self.tiles[0][0] is None:
            logger.debug("> SudokuBoard::update_board_values - Board not initialized, creating board")
            self._create_board(board)
            return
        
        # If board exists, update the values safely
        try:
            # If board exists, just update the values
            for row in range(9):
                for col in range(9):
                    tile = self.tiles[row][col]
                    # Check if the tile's widgets still exist by accessing a property
                    try:
                        tile.frame.winfo_exists()
                        tile.set_value(board[row][col])
                        # If the tile is fixed, set it to fixed
                        if board[row][col] != 0:
                            tile.is_fixed = True
                            tile.label.config(bg="#f0f0f0")
                        else:
                            tile.is_fixed = False
                            tile.label.config(bg="white")
                    except (tk.TclError, AttributeError):
                        logger.warning(">> SudokuBoard::update_board_values - Tile widget no longer exists at position (%d, %d)", row, col)
                        # This indicates we should recreate the board
                        return
                        
            # Clear selected position and highlights
            self.selected_pos = None
            self.clear_highlights()
        except Exception as e:
            logger.error(">>>> SudokuBoard::update_board_values - Error updating board: %s", str(e))
            # If we encounter any errors, recreate the board
            for box in self.frame.winfo_children():
                box.destroy()
            self.tiles = [[None for _ in range(9)] for _ in range(9)]
            self._create_board(board)

    def reset_board(self):
        """
        Reset the board's internal state by clearing all tile references and widgets.
        This ensures a fresh board will be created when update_board_values is called.
        """
        logger.debug("> SudokuBoard::reset_board - Resetting board state")
        
        # Clear all tile references
        self.tiles = [[None for _ in range(9)] for _ in range(9)]
        
        # Clear selected position
        self.selected_pos = None

    def _handle_tile_click(self, row, col):
        """
        Handle tile click events.

        Args:
            row: Row index of clicked tile
            col: Column index of clicked tile
        """
        logger.debug(f">>>SudokuBoard::_handle_tile_click - Tile clicked at ({row}, {col})")

        # Deselect previously selected tile
        if self.selected_pos:
            prev_row, prev_col = self.selected_pos
            self.tiles[prev_row][prev_col].select(False)

        # Select the newly clicked tile
        self.selected_pos = (row, col)
        self.tiles[row][col].select(True)

        self._highlight_matching_values(row, col)
        self._highlight_not_possible_locations(row, col)

        # Call the external click handler
        if self.on_tile_click:
            self.on_tile_click(row, col)

    def _highlight_matching_values(self, row, col):
        """
        Highlight the row, column, and matching values of the selected tile.

        Args:
            row: Row index of selected tile
            col: Column index of selected tile
        """
        logger.debug(f">>>SudokuBoard::_highlight_matching_values - Highlighting for cell ({row}, {col})")

        # Clear previous highlights
        for r in range(9):
            for c in range(9):
                if (r, c) != (row, col):  # Don't clear selection highlight
                    self.tiles[r][c].highlight(False)

        matching_blue = "#e1f5fe"
        selected_value = self.tiles[row][col].value

        # Skip value highlighting if selected cell is empty
        if selected_value == 0:
            return

        # Highlight matching values with a more noticeable blue
        # but only if they're not already in the highlighted row/column
        for r in range(9):
            for c in range(9):
                if ((r, c) != (row, col) and r != row and c != col and self.tiles[r][c].value == selected_value):
                    self.tiles[r][c].highlight(True, matching_blue)

    def _highlight_not_possible_locations(self, row, col):
        """
        Highlight cells that cannot contain the same value as the selected cell
        (cells in the same row, column, and 3x3 box).

        Args:
            row: Row index of selected tile
            col: Column index of selected tile
        """
        light_color = "#fff8e7"
        for r in range(9):
            for c in range(9):
                # Skip the selected cell
                if (r, c) == (row, col):
                    continue

                # Highlight cells in the same row
                if r == row:
                    self.tiles[r][c].highlight(True, light_color)

                # Highlight cells in the same column
                elif c == col:
                    self.tiles[r][c].highlight(True, light_color)

                # Highlight cells in the same 3x3 box
                elif (r // 3 == row // 3) and (c // 3 == col // 3):
                    self.tiles[r][c].highlight(True, light_color)

    def flash_cell(self, row, col, color="red", duration=UIManager.FLASH_DURATION_MS):
        """
        Flash a cell with a color temporarily.

        Args:
            row: Row index (0-8)
            col: Column index (0-8)
            color: Color to flash
            duration: Duration of flash in milliseconds
        """
        self.tiles[row][col].flash(color, duration)

    def clear_highlights(self):
        """
        Clear all highlights on the board.
        """
        logger.debug(">>>SudokuBoard::clear_highlights - Clearing all highlights")
        for row in range(9):
            for col in range(9):
                self.tiles[row][col].highlight(False)

    def get_selected_position(self):
        """
        Get the currently selected position.

        Returns:
            tuple: (row, col) or None if no cell is selected
        """
        return self.selected_pos

    def clear_highlights(self):
        """
        Clear all highlights on the board.
        """
        logger.debug(">>>SudokuBoard::clear_highlights - Clearing all highlights")
        for row in range(9):
            for col in range(9):
                self.tiles[row][col].highlight(False)

    def get_selected_position(self):
        """
        Get the currently selected position.

        Returns:
            tuple: (row, col) or None if no cell is selected
        """
        return self.selected_pos

    def disable_board(self):
        """Disable all interaction with the board."""
        logger.debug(">>>SudokuBoard::disable_board - Disabling all board interactions")
        for row in range(9):
            for col in range(9):
                tile = self.tiles[row][col]
                tile.label.config(bg="grey")
                tile.label.unbind("<Button-1>")
                tile.frame.unbind("<Button-1>")
                tile.on_click = None
                tile.frame.bind("<Button-1>", lambda e: None)
                # Note: root unbinding should happen in the window class, not here
                tile.label.update()


class ButtonPanel:
    """
    A panel containing buttons for starting a new game, solving the puzzle, and exiting the game.
    """

    def __init__(self, parent):
        """
        Initialize the button panel.

        Args:
            parent: The parent widget.
            on_new_game: Callback function for the "New Game" button.
            on_solve: Callback function for the "Solve" button.
            on_exit: Callback function for the "Exit" button.
        """
        logger.debug(">>>ButtonPanel::init - Initializing ButtonPanel")

        self.frame = tk.Frame(parent, padx=10, pady=10)

        self.new_game_button = tk.Button(
            self.frame,
            text="New Game",
            command=self._confirm_new_game,
            width=15,
            height=2,
        )
        self.new_game_button.pack(pady=5)

        # Create the "Solve" button
        self.solve_button = tk.Button(self.frame, text="Solve", command=self._on_solve, width=15, height=2)
        self.solve_button.pack(pady=5)

        # Create the "Exit" button
        self.exit_button = tk.Button(self.frame, text="Exit", command=self._on_exit, width=15, height=2)
        self.exit_button.pack(pady=5)

    def _confirm_new_game(self):
        """
        Ask the user for confirmation before starting a new game.

        Returns:
            bool: True if the user confirms, False otherwise.
        """
        logger.debug(">>>ButtonPanel::confirm_new_game - Asking for confirmation to start a new game")
        response = tk.messagebox.askyesno("New Game", "Are you sure you want to start a new game?")
        # if yes, then call the command
        if response:
            logger.info(">>>ButtonPanel::confirm_new_game - User confirmed new game")
            # Record button click in metrics
            metrics = get_metrics_service()
            if metrics:
                metrics.record_button_click("new_game")
            self.new_game_button.event_generate(UIManager.NEW_GAME_REQUEST_EVENT)
        else:
            logger.debug(">>>ButtonPanel::confirm_new_game - User canceled new game")
        return response

    def _on_solve(self):
        """
        Handle the "Solve" button click.
        """
        logger.debug(">>>ButtonPanel::_on_solve - Solve button clicked")
        # Record button click in metrics
        metrics = get_metrics_service()
        if metrics:
            metrics.record_button_click("solve")
        self.solve_button.event_generate(UIManager.SOLVE_REQUEST_EVENT)

    def _on_exit(self):
        """
        Handle the "Exit" button click.
        """
        logger.debug(">>>ButtonPanel::_on_exit - Exit button clicked")
        # Record button click in metrics
        metrics = get_metrics_service()
        if metrics:
            metrics.record_button_click("exit")
        self.exit_button.event_generate(UIManager.EXIT_GAME_REQUEST_EVENT)


class DifficultySelector:
    """
    A frame containing a combo box for selecting the difficulty level.
    """

    def __init__(self, parent, on_difficulty_change):
        """
        Initialize the difficulty selector.

        Args:
            parent: The parent widget.
            on_difficulty_change: Callback function for when the difficulty is changed.
        """
        logger.debug(">>>DifficultySelector::init - Initializing DifficultySelector")
        self.frame = tk.Frame(parent, padx=10, pady=10)

        # Label for the difficulty selector - now positioned above the dropdown
        self.label = tk.Label(self.frame, text="Select Difficulty:", font=("Arial", 12))
        # Add padding at bottom
        self.label.pack(side=tk.TOP, padx=5, pady=(0, 5))

        # Combo box for difficulty selection
        self.difficulty_var = tk.StringVar(value=Difficulty.MEDIUM.value)
        self._previous_difficulty = Difficulty.MEDIUM.value
        self._set_difficulty(Difficulty.MEDIUM)
        self.combo_box = tk.OptionMenu(
            self.frame,
            self.difficulty_var,
            *[difficulty.value for difficulty in Difficulty],
            command=on_difficulty_change,
        )
        # Increased width for better appearance
        self.combo_box.config(width=15)
        self.combo_box.pack(side=tk.TOP, padx=5)

    def reset_difficulty(self):
        """
        Reset the difficulty level to the previous selection.
        """
        logger.debug(f">>>DifficultySelector::reset_difficulty - Resetting difficulty to {self._previous_difficulty}")
        self.difficulty_var.set(self._previous_difficulty)
        self._set_difficulty(Difficulty(self._previous_difficulty))

    def _set_difficulty(self, difficulty):
        """
        Set the difficulty level in the combo box.

        Args:
            difficulty: The difficulty level to set.
        """
        logger.debug(f">>>DifficultySelector::set_difficulty - Setting difficulty to {difficulty}")
        self.difficulty_var.set(difficulty.value)
        self._previous_difficulty = difficulty.value
        
        # Record button click in metrics
        metrics = get_metrics_service()
        if metrics:
            metrics.record_button_click(f"difficulty_{difficulty.value.lower()}")

    def get_difficulty(self):
        """
        Get the currently selected difficulty level.

        Returns:
            str: The selected difficulty level.
        """
        logger.debug(f">>>DifficultySelector::get_difficulty - Current difficulty: {self.difficulty_var.get()}")
        return self.difficulty_var.get()


class NumberPanel:
    """
    A panel containing number cells (frames) for numbers 1 to 9, allowing keyboard-less gaming
    and showing feedback on how many of each number are left to be placed.
    """

    def __init__(self, parent, on_number_click):
        """
        Initialize the number panel.

        Args:
            parent: The parent widget.
            on_number_click: Callback function when a number is clicked.
        """
        logger.debug(">>>NumberPanel::init - Initializing NumberPanel")
        # Create a container frame
        self.frame = tk.Frame(parent)
        self.on_number_click = on_number_click

        # Create frames for numbers 1 to 9 instead of buttons
        self.panels = {}
        for number in range(1, 10):
            # Create a frame for each number with white background
            number_frame = tk.Frame(
                self.frame,
                borderwidth=2,
                relief=tk.RAISED,
                bg="white",  # White background by default
            )

            # Create a label inside the frame to display the number and count
            number_label = tk.Label(
                number_frame,
                text=f"{number}\n(9)",
                font=("Arial", 11),
                bg="white",  # Same as frame background
            )
            number_label.pack(expand=True, fill=tk.BOTH, padx=2, pady=2)

            # Grid the frame in the container
            number_frame.grid(row=0, column=number - 1, sticky=tk.NSEW, padx=1, pady=2)
            self.panels[number] = {
                "frame": number_frame,
                "label": number_label,
            }

        self.enable_all()

        # Configure grid to make columns equal width
        for i in range(9):
            self.frame.columnconfigure(i, weight=1, uniform="equal")

        # Configure row to expand and fill available space
        self.frame.rowconfigure(0, weight=1)

    def enable_all(self):
        for number in range(1, 10):
            components = self.panels[number]
            number_frame = components["frame"]
            number_label = components["label"]
            number_frame.bind("<Button-1>", lambda e, n=number: self._handle_number_click(n))
            number_label.bind("<Button-1>", lambda e, n=number: self._handle_number_click(n))

    def disable_all(self):
        # disable all frames and labels, update the self.panels dictionary
        logger.debug(">>>NumberPanel::disable_all - Disabling all number panels")
        for number in range(1, 10):
            components = self.panels[number]
            frame = components["frame"]
            label = components["label"]
            frame.config(bg="#f0f0f0")  # Light gray
            label.config(bg="#f0f0f0", fg="#a0a0a0")  # Gray text on light gray background
            components["enabled"] = False
            # Force update
            label.update()
            frame.update()
            logger.debug(f">>>NumberPanel::disable_all - Number {number} disabled")
            # Disable click events
            frame.unbind("<Button-1>")
            label.unbind("<Button-1>")

    def set_width(self, width):
        """
        Set the width of the number panel to match the specified width.

        Args:
            width: The width to match (from the Sudoku board)
        """
        logger.debug(f">>>NumberPanel::set_width - Setting panel width to {width}")

        # Ensure width is an integer
        width = int(width)

        # Direct configuration of the frame width
        self.frame.config(width=width, height=60)

        # Make sure the frame doesn't propagate its size from its children
        self.frame.pack_propagate(False)
        self.frame.grid_propagate(False)
        actual_width = self.frame.winfo_width()

        # Distribute the width equally among the number cells
        cell_width = width // 9
        for number in range(1, 10):
            # Adjust each number frame to have an equal share of the width
            self.panels[number]["frame"].config(width=cell_width)

    def _handle_number_click(self, number):
        """
        Handle number click events.

        Args:
            number: The number clicked.
        """
        logger.debug(f">>>NumberPanel::_handle_number_click - Number {number} clicked")

        # Only respond to clicks if the panel is enabled
        if number in self.panels and self.panels[number]["enabled"]:
            # Record button click in metrics
            metrics = get_metrics_service()
            if metrics:
                metrics.record_button_click(f"number_{number}")
                
            # Provide visual feedback for the click
            self._flash_panel(number)

            if self.on_number_click:
                self.on_number_click(number)
        else:
            logger.debug(f">>>NumberPanel::_handle_number_click - Number {number} is disabled, ignoring click")

    def _flash_panel(self, number):
        """
        Provide visual feedback when a number is clicked.

        Args:
            number: The number that was clicked
        """
        if number not in self.panels or not self.panels[number]["enabled"]:
            return

        components = self.panels[number]
        frame = components["frame"]
        label = components["label"]

        orig_bg = frame.cget("bg")

        flash_bg = "#e0e0e0"  # Light gray for flash effect

        frame.config(bg=flash_bg)
        label.config(bg=flash_bg)

        self.frame.after(100, lambda: frame.config(bg=orig_bg))
        self.frame.after(100, lambda: label.config(bg=orig_bg))

    def update_all_numbers(self, numbers):
        """
        Update the number panel with the current numbers.

        Args:
            numbers: A dictionary with keys from 1 to 9 and their respective counts.
        9 is the maximum number of times a number can be placed.
        0 is the minimum number of times a number can be placed.
        9 - count is the number of times this number has been placed.
        0 - count is the number of times this number has not been placed.
        """
        logger.debug(f">>>NumberPanel::update_all_numbers - Updating all numbers: {numbers}")
        for number in range(1, 10):
            self.update_number_count(number, numbers.get(number, 0))
        logger.debug(">>>NumberPanel::update_all_numbers - All numbers updated")

    def update_number_count(self, number, count):
        """
        Update the count of how many of a specific number are left to be placed.

        Args:
            number: The number to update.
            count: The number of times this number has been placed.
        """
        if number in self.panels:
            if count < 0:
                count = 0
            elif count > 9:
                count = 9
        # Calculate remaining count (9 - placed)
        remaining = 9 - count

        components = self.panels[number]
        frame = components["frame"]
        label = components["label"]

        # Set text with remaining count
        label.config(text=f"{number}\n({remaining})")

        if remaining <= 0:
            # Disable the panel - gray it out
            frame.config(bg="#f0f0f0")  # Light gray
            label.config(bg="#f0f0f0", fg="#a0a0a0")  # Gray text on light gray background
            self.panels[number]["enabled"] = False
        else:
            # Enable the panel - white background with black text
            frame.config(bg="white")
            label.config(bg="white", fg="black")
            self.panels[number]["enabled"] = True

class InfoPanel:
    """
    A panel to display game information like time, moves, and wrong moves.
    """

    def __init__(self, parent):
        """
        Initialize the info panel.

        Args:
            parent: The parent widget.
        """
        logger.debug(">>>InfoPanel::init - Initializing InfoPanel")
        self.frame = tk.Frame(parent, pady=5)

        # Configure grid layout for the info panel frame
        self.frame.columnconfigure(0, weight=1)  # Label column
        self.frame.columnconfigure(1, weight=1)  # Value column
        self.frame.columnconfigure(2, weight=1)  # Label column
        self.frame.columnconfigure(3, weight=1)  # Value column
        self.frame.columnconfigure(4, weight=1)  # Label column
        self.frame.columnconfigure(5, weight=1)  # Value column

        # Time display
        tk.Label(self.frame, text="Time:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.E, padx=(0, 2))
        self.time_label = tk.Label(self.frame, text="00:00", font=("Arial", 10, "bold"))
        self.time_label.grid(row=0, column=1, sticky=tk.W, padx=(2, 10))

        # Moves display
        tk.Label(self.frame, text="Moves:", font=("Arial", 10)).grid(row=0, column=2, sticky=tk.E, padx=(0, 2))
        self.moves_label = tk.Label(self.frame, text="0", font=("Arial", 10, "bold"))
        self.moves_label.grid(row=0, column=3, sticky=tk.W, padx=(2, 10))

        # Wrong Moves display
        tk.Label(self.frame, text="Mistakes:", font=("Arial", 10)).grid(row=0, column=4, sticky=tk.E, padx=(0, 2))
        self.wrong_moves_label = tk.Label(self.frame, text=f"0/{MAX_WRONG_MOVES}", font=("Arial", 10, "bold"))
        self.wrong_moves_label.grid(row=0, column=5, sticky=tk.W, padx=(2, 0))

    def update_time(self, elapsed_time_str):
        """Update the time display."""
        self.time_label.config(text=elapsed_time_str)
        # self.time_label.update_idletasks()  # Ensure immediate update

    def update_moves(self, moves):
        """Update the moves display."""
        self.moves_label.config(text=str(moves))
        # self.moves_label.update_idletasks()

    def update_wrong_moves(self, wrong_moves):
        """Update the wrong moves display."""
        self.wrong_moves_label.config(text=f"{wrong_moves}/{MAX_WRONG_MOVES}")
        # self.wrong_moves_label.update_idletasks()

    def reset(self):
        """Reset all displays to their initial state."""
        logger.debug(">>>InfoPanel::reset - Resetting info panel displays")
        self.update_time("00:00")
        self.update_moves(0)
        self.update_wrong_moves(0)


class OptionsPanel:
    """
    A panel containing options like Notes Mode and Automatic Notes Mode.
    """

    def __init__(self, parent):
        """
        Initialize the options panel.

        Args:
            parent: The parent widget.
            on_notes_mode_change: Callback for Notes Mode checkbox.
            on_auto_notes_mode_change: Callback for Automatic Notes Mode checkbox.
        """
        logger.debug(">>>OptionsPanel::init - Initializing OptionsPanel")
        self._frame = tk.Frame(parent, padx=10, pady=10)

        # Notes Mode checkbox
        self.notes_mode_var = tk.BooleanVar(value=False)
        self.notes_mode_checkbox = tk.Checkbutton(
            self._frame,
            text="Notes Mode",
            variable=self.notes_mode_var,
            command=self._on_notes_mode_selected,  # Use command instead of bind
        )
        self.notes_mode_checkbox.pack(anchor=tk.W, pady=2)

        # Automatic Notes Mode checkbox
        self.auto_notes_mode_var = tk.BooleanVar(value=False)
        self.auto_notes_mode_checkbox = tk.Checkbutton(
            self._frame,
            text="Automatic Notes Mode",
            variable=self.auto_notes_mode_var,
            command=self._on_auto_notes_mode_selected,
        )
        self.auto_notes_mode_checkbox.pack(anchor=tk.W, pady=2)

    def _on_notes_mode_selected(self):
        """
        Handle selection events for the Notes Mode checkbox.
        """
        logger.debug(
            ">>>OptionsPanel::_on_notes_mode_selected - Notes Mode selected with value of: [%s]",
            self.notes_mode_var.get(),
        )
        
        # Record button click in metrics
        metrics = get_metrics_service()
        if metrics:
            metrics.record_button_click("notes_mode_toggle")

        self.notes_mode_checkbox.event_generate(UIManager.NOTES_MODE_REQUEST_EVENT, when="tail")


    def _on_auto_notes_mode_selected(self):
        """
        Handle selection events for the Auto Notes Mode checkbox.
        """
        logger.debug(
            ">>>OptionsPanel::_on_auto_notes_mode_selected - Notes Mode selected with value of: [%s]",
            self.auto_notes_mode_var.get(),
        )
        
        # Record button click in metrics
        metrics = get_metrics_service()
        if metrics:
            metrics.record_button_click("auto_notes_mode_toggle")
            
        self.auto_notes_mode_checkbox.event_generate(UIManager.AUTO_NOTES_MODE_REQUEST_EVENT, when="tail")
