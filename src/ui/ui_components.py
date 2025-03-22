import tkinter as tk
from typing import Callable, List
from ui.formatters import BasicStatsFormatter, StatsFormatter
from core.difficulty import Difficulty  # Add this import
from typing import List, Optional, Tuple, Callable

class SudokuTile:
    """Represents a single tile in the Sudoku grid."""
    
    def __init__(self, parent, row: int, col: int, size: int, value: int, on_click_callback: Callable):
        """
        Initialize a tile.
        
        Args:
            parent: The parent widget
            row: The tile's row in the 9x9 grid
            col: The tile's column in the 9x9 grid
            size: The size of the tile in pixels
            on_click_callback: Function to call when tile is clicked
        """
        self.row = row
        self.col = col
        self.value = value if value is not None else 0
        self.is_fixed = False
        self.is_selected = False
        self.on_click = on_click_callback
        
        # Create the frame for the tile
        self.frame = tk.Frame(
            parent,
            width=size,
            height=size,
            borderwidth=1,
            relief=tk.RAISED
        )
        self.frame.grid_propagate(False)  # Keep the frame size fixed
        
        # Create the label for displaying the value
        self.label = tk.Label(
            self.frame,
            font=("Arial", 18, "bold"),
            width=2,
            height=1,
            bg="white"
        )
        self.label.pack(expand=True, fill=tk.BOTH)
        
        # Bind the click event
        self.label.bind("<Button-1>", self._handle_click)
    
    def _handle_click(self, event):
        """Handle click events on the tile."""
        self.on_click(self.row, self.col)
    
    def set_value(self, value: int, is_fixed: bool = False):
        """Set the tile's value and whether it's a fixed (original) tile."""
        self.value = value
        self.is_fixed = is_fixed
        self.update_display()
    
    def set_selected(self, selected: bool):
        """Mark the tile as selected or not."""
        self.is_selected = selected
        self.update_display()
    
    def update_display(self):
        """Update the tile's appearance based on its state."""
        # Update the displayed text
        self.label.config(text="" if self.value == 0 else str(self.value))
        
        # Set the appropriate colors based on state
        if self.is_selected:
            self.label.config(bg="#c5e1e8")  # Light blue for selection
        elif self.is_fixed:
            self.label.config(bg="#f0f0f0", fg="black")  # Gray for fixed tiles
        else:
            self.label.config(bg="white", fg="blue")  # Blue text for user entries
    
    def grid(self, **kwargs):
        """Grid the tile using the frame's grid method."""
        self.frame.grid(**kwargs)
    
    def flash_invalid(self):
        """Flash the tile to indicate an invalid move."""
        original_bg = self.label.cget("bg")
        self.label.config(bg="red")
        self.label.after(500, lambda: self.label.config(bg=original_bg))
    
    def highlight(self, bg_hex_color="#d4edda"):
        """Highlight the tile with light green background."""
        self.label.config(bg=bg_hex_color)  # Light green for highlighting
    
    def clear_highlight(self):
        """Clear the highlight from the tile."""
        self.update_display()

class NumberTile:
    """Represents a single tile in the number panel."""
    
    def __init__(self, parent, number: int, on_click_callback: Callable):
        """
        Initialize a number tile.
        
        Args:
            parent: The parent widget
            number: The number to display
            on_click_callback: Function to call when tile is clicked
        """
        self.number = number
        self.count = 9  # Initially, each number can appear 9 times
        self.on_click = on_click_callback
        
        # Create the frame for the tile
        self.frame = tk.Frame(
            parent,
            width=40,
            height=40,
            borderwidth=2,
            relief=tk.RAISED,
            bg="#f0f0f0"
        )
        self.frame.grid_propagate(False)  # Keep the frame size fixed
        
        # Create the label for displaying the number
        self.number_label = tk.Label(
            self.frame,
            text=str(self.number),
            font=("Arial", 14, "bold"),
            bg="#f0f0f0"
        )
        self.number_label.pack(expand=True, fill=tk.BOTH)
        
        # Create the label for displaying the count
        self.count_label = tk.Label(
            self.frame,
            text=f"({self.count})",
            font=("Arial", 8),
            bg="#f0f0f0"
        )
        self.count_label.pack(side=tk.BOTTOM)
        
        # Bind the click event
        self.frame.bind("<Button-1>", self._handle_click)
        self.number_label.bind("<Button-1>", self._handle_click)
        self.count_label.bind("<Button-1>", self._handle_click)
    
    def _handle_click(self, event):
        """Handle click events on the tile."""
        self.on_click(self.number)
    
    def update_count(self, count: int):
        """Update the count of the number."""
        self.count = count
        self.count_label.config(text=f"({self.count})")
        if self.count == 0:
            self.number_label.config(fg="#f0f0f0")  # Hide the number by changing its color to the background color
        else:
            self.number_label.config(fg="black")  # Show the number in black color
    
    def grid(self, **kwargs):
        """Grid the tile using the frame's grid method."""
        self.frame.grid(**kwargs)


class NumberPanel:
    """Panel to display number tiles with their counters."""
    
    def __init__(self, parent, on_tile_click: Callable):
        """
        Initialize the number panel.
        
        Args:
            parent: The parent widget
            on_tile_click: Function to call when a tile is clicked
        """
        self.frame = tk.Frame(parent)
        self.frame.grid(row=3, column=0, columnspan=9, pady=(10, 0), sticky="ew")
        
        self.tiles: List[NumberTile] = []
        for number in range(1, 10):
            tile = NumberTile(self.frame, number, on_tile_click)
            tile.grid(row=0, column=number-1, padx=2)
            self.tiles.append(tile)
    
    def update_counts(self, counts: List[int]):
        """Update the counts of all number tiles."""
        print("Counts:",counts)
        for number, count in enumerate(counts, start=1):
            self.tiles[number-1].update_count(count)

class StatsWindow:
    """Popup window to display game stats."""
    
    def __init__(self, parent, controller, initial_difficulty: Difficulty = None, formatter: StatsFormatter = None):
        """
        Initialize stats window.
        
        Args:
            parent: Parent window
            controller: Game controller
            initial_difficulty: Initial difficulty to display stats for (default from game if not provided)
            formatter: Stats formatter instance
        """
        self.controller = controller
        self.formatter = formatter or BasicStatsFormatter()
        self.window = tk.Toplevel(parent)
        self.window.title("Game Stats")
        
        # Use provided initial difficulty or default to EASY
        initial_diff_value = initial_difficulty.value if initial_difficulty else Difficulty.EASY.value
        self.difficulty = tk.StringVar(value=initial_diff_value)
        
        # Create difficulty selection dropdown
        tk.Label(self.window, text="Difficulty:").pack(side=tk.LEFT, padx=5, pady=5)
        difficulty_combo = ttk.Combobox(
            self.window,
            textvariable=self.difficulty,
            values=[difficulty.value for difficulty in Difficulty],
            state="readonly",
            width=10
        )
        difficulty_combo.pack(side=tk.LEFT, padx=5, pady=5)
        difficulty_combo.bind("<<ComboboxSelected>>", self.update_stats_display)
        
        # Create stats label with monospace font for better alignment
        self.stats_label = tk.Label(
            self.window, 
            text="", 
            justify=tk.LEFT, 
            font=("Courier", 10),
            anchor="w"
        )
        self.stats_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Initial display
        self.update_stats_display()
    
    def update_stats_display(self, event=None):
        """Update the stats display based on the selected difficulty."""
        difficulty = Difficulty(self.difficulty.get())
        stats = self.controller.get_stats(difficulty)
        
        # Use the formatter to format the stats
        formatted_stats = self.formatter.format_stats(difficulty, stats)
        
        self.stats_label.config(text=formatted_stats)

class SudokuBoard:
    """Represents the Sudoku board with 9x9 tiles."""
    
    def __init__(self, parent, on_tile_click: Callable):
        """
        Initialize the Sudoku board.
        
        Args:
            parent: The parent widget
            on_tile_click: Function to call when a tile is clicked
        """
        self.parent = parent
        self.on_tile_click = on_tile_click
        self.tiles = [[None for _ in range(9)] for _ in range(9)]
        self._create_board()
    
    def _create_board(self):
        """Create the Sudoku board with boxes and tiles."""
        self.boxes = []
        for box_row in range(3):
            for box_col in range(3):
                box = tk.Frame(
                    self.parent, 
                    borderwidth=2,
                    relief=tk.RAISED
                )
                box.grid(row=box_row, column=box_col, padx=1, pady=1)
                self.boxes.append(box)
                
                for cell_row in range(3):
                    for cell_col in range(3):
                        row = box_row * 3 + cell_row
                        col = box_col * 3 + cell_col
                        tile = SudokuTile(
                            box, 
                            row, 
                            col, 
                            50,  # Assuming cell size is 50
                            0,
                            self.on_tile_click
                        )
                        tile.grid(row=cell_row, column=cell_col)
                        self.tiles[row][col] = tile
    
    def update_board(self, board: List[List[int]], selected_cell: Optional[Tuple[int, int]] = None):
        """Update the UI to reflect the current game state."""
        selected_value = None
        if selected_cell:
            selected_row, selected_col = selected_cell
            selected_value = board[selected_row][selected_col]
        
        for row in range(9):
            for col in range(9):
                tile = self.tiles[row][col]
                is_selected = selected_cell and (row, col) == selected_cell
                tile.set_selected(is_selected)
                value = board[row][col]
                is_fixed = value != 0
                tile.set_value(value, is_fixed)
                if selected_value and selected_value != 0 and value == selected_value and not is_selected:
                    tile.highlight("#e1f5fe")
