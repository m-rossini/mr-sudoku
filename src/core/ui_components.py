import tkinter as tk
import logging
from core.controller import ControllerDependent

logger = logging.getLogger(__name__)

class UIManager(ControllerDependent):
    def __init__(self, root):
        logger.debug(">>>UIManager::init - Initializing UIManager")
        self.root = root
        
        # Main frame for all components
        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Create the Sudoku board
        self.board = SudokuBoard(self.main_frame, self._on_tile_click)
        self.board.frame.pack(padx=10, pady=10)
        
    def set_controller(self, controller):
        """
        Set the controller for this UIManager.
        
        Args:
            controller: The controller instance.
        """
        logger.debug(">>>UIManager::set_controller - Setting controller")
        self.controller = controller
    
    def start_game(self, board):
        """
        Start a new game by displaying the Sudoku board.
        
        Args:
            board: The Sudoku board to display.
        """
        logger.debug(">>>UIManager::start_game - Starting new game")
        self.board._create_board(board)
        
    def _on_tile_click(self, row, col):
        """Handle tile click events."""
        logger.debug(f">>>UIManager::_on_tile_click - Tile clicked at position ({row}, {col})")
    
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
        
        # Create the tile frame
        self.frame = tk.Frame(
            parent,
            width=50,
            height=50,
            borderwidth=1,
            relief=tk.RAISED
        )
        
        # Keep the frame size fixed
        self.frame.grid_propagate(False)
        
        # Create the tile label for displaying the value
        self.label = tk.Label(
            self.frame,
            text="",
            font=("Arial", 18, "bold"),
            width=2,
            height=1,
            bg="white"
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
        
        # Update the display text
        if value == 0:
            self.label.config(text="")
        else:
            self.label.config(text=str(value))
        
        # Set the appropriate styling
        if self.is_fixed:
            # Fixed values have black text on light gray background
            self.label.config(fg="black", bg="#f0f0f0")
        else:
            # User-entered or empty values have blue text on white background
            self.label.config(fg="blue", bg="white")
    
    def select(self, selected=True):
        """
        Select or deselect this tile.
        
        Args:
            selected: Whether the tile should be selected
        """
        self.is_selected = selected
        if selected:
            self.label.config(bg="#c5e1e8")  # Light blue background for selected tile
        else:
            # When deselected, go back to fixed or normal background
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
            # When not highlighted, go back to fixed or normal background
            if self.is_fixed:
                self.label.config(bg="#f0f0f0")  # Light gray for fixed values
            else:
                self.label.config(bg="white")    # White for regular cells
    
    def flash(self, color="red", duration=500):
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
    
    def __init__(self, parent, on_tile_click=None):
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
    
    def _create_board(self, board):
        """Create the 9x9 Sudoku board with 3x3 boxes."""
        # Create the 3x3 boxes
        for box_row in range(3):
            for box_col in range(3):
                # Create a box with a thicker border
                box = tk.Frame(
                    self.frame,
                    borderwidth=2,
                    relief=tk.RAISED
                )
                box.grid(row=box_row, column=box_col, padx=1, pady=1)
                
                # Create the 3x3 tiles within each box
                for cell_row in range(3):
                    for cell_col in range(3):
                        # Calculate global row and column
                        row = box_row * 3 + cell_row
                        col = box_col * 3 + cell_col
                        
                        # Create the tile
                        tile = SudokuTile(box, row, col,value=board[row][col], on_click=self._handle_tile_click)
                        tile.frame.grid(row=cell_row, column=cell_col)
                        # Store reference to the tile
                        self.tiles[row][col] = tile
        
        logger.debug(">>>SudokuBoard::_create_board - Board created with 9x9 grid")
    
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
        
        # Highlight tiles with the same value
        self._highlight_matching_values(row, col)
        
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
        
        # Very light blue for row/column highlighting
        very_light_blue = "#deebf0"  # Extremely light blue
        
        # Medium light blue for value matching
        matching_blue = "#e1f5fe"
        
        # First, highlight the row and column
        for r in range(9):
            for c in range(9):
                # Skip the selected cell
                if (r, c) == (row, col):
                    continue
                    
                # Highlight cells in the same row
                if r == row:
                    self.tiles[r][c].highlight(True, very_light_blue)
                
                # Highlight cells in the same column
                elif c == col:
                    self.tiles[r][c].highlight(True, very_light_blue)
        
        # Get the selected value
        selected_value = self.tiles[row][col].value
        
        # Skip value highlighting if selected cell is empty
        if selected_value == 0:
            return
        
        # Highlight matching values with a more noticeable blue
        # but only if they're not already in the highlighted row/column
        for r in range(9):
            for c in range(9):
                if (r, c) != (row, col) and r != row and c != col and self.tiles[r][c].value == selected_value:
                    self.tiles[r][c].highlight(True, matching_blue)
    
    def flash_cell(self, row, col, color="red", duration=500):
        """
        Flash a cell with a color temporarily.
        
        Args:
            row: Row index (0-8)
            col: Column index (0-8)
            color: Color to flash
            duration: Duration of flash in milliseconds
        """
        self.tiles[row][col].flash(color, duration)
    
    def get_selected_position(self):
        """
        Get the currently selected position.
        
        Returns:
            tuple: (row, col) or None if no cell is selected
        """
        return self.selected_pos
