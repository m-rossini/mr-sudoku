import tkinter as tk
from tkinter import ttk  # Add this import for themed widgets
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
            self.label.config(bg="white")  

    def grid(self, **kwargs):
        """Grid the tile using the frame's grid method."""
        self.frame.grid(**kwargs)
    
    def flash(self, color: str, duration: int = 500):
        """Flash the tile with the given color for a specified duration."""
        original_bg = self.label.cget("bg")
        self.label.config(bg=color)
        self.label.after(duration, lambda: self.label.config(bg=original_bg))

    def flash_invalid(self):
        """Flash the tile to indicate an invalid move."""
        self.flash("red")

    def flash_warning(self):
        """Flash the tile to indicate a warning."""
        self.flash("orange")

    def highlight(self, bg_hex_color="#d4edda"):
        """Highlight the tile with light green background."""
        self.label.config(bg=bg_hex_color)  # Light green for highlighting
    
    def clear_highlight(self):
        """Clear the highlight from the tile."""
        self.update_display()

class NumberTile:
    """A tile displaying a number and its remaining count."""
    
    def __init__(self, parent, number: int, on_click: Callable):
        """Initialize the number tile."""
        self.frame = tk.Frame(parent)
        self.number = number
        self.on_click = lambda: on_click(number)
        
        # Create the tile with a border
        self.tile = tk.Label(
            self.frame, 
            text=str(number),
            font=("Arial", 16, "bold"),
            width=2,
            bd=1,
            relief=tk.RAISED,
            bg="#e0e0e0"
        )
        # Use grid instead of pack for internal widgets
        self.tile.grid(row=0, column=0, sticky="nsew")
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.tile.bind("<Button-1>", lambda e: self.on_click())
        
        # Create the counter beneath the tile
        self.counter = tk.Label(self.frame, text="9", font=("Arial", 10))
        self.counter.grid(row=1, column=0)  # Use grid instead of pack
        
        # These allow the tile to be added to a parent with either method
        self.grid = self.frame.grid
        self.pack = self.frame.pack
    
    def update_count(self, count: int):
        """Update the count of the number."""
        self.count = count
        self.counter.config(text=f"({self.count})")
        if self.count == 0:
            self.tile.config(fg="#f0f0f0")  # Hide the number by changing its color to the background color
        else:
            self.tile.config(fg="black")  # Show the number in black color


class NumberPanel:
    def __init__(self, parent, on_tile_click: Callable):
        self.frame = tk.Frame(parent)
        
        # Configure grid for the number tiles
        for i in range(9):
            self.frame.columnconfigure(i, weight=1)
        
        # Create tiles using grid
        self.tiles = []
        for number in range(1, 10):
            tile = NumberTile(self.frame, number, on_tile_click)
            tile.grid(row=0, column=number-1, padx=3, sticky="ew")
            self.tiles.append(tile)
        
    def update_counts(self, counts: List[int]):
        """Update the counts of all number tiles."""
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

class ControlPanel:
    """Panel to display game controls."""

    def __init__(self, parent, new_game_command: Callable, check_command: Callable, solve_command: Callable, stats_command: Callable):
        """
        Initialize the control panel.

        Args:
            parent: The parent widget
            new_game_command: Function to call when the new game button is clicked
            check_command: Function to call when the check button is clicked
            solve_command: Function to call when the solve button is clicked
            stats_command: Function to call when the stats button is clicked
        """
        self.frame = tk.Frame(parent)
        self.new_game_command = new_game_command
        self.check_command = check_command
        self.solve_command = solve_command
        self.stats_command = stats_command
        self._create_widgets()

    def _create_widgets(self):
        """Create the control buttons with even spacing."""
        # Create a container frame with proper padding
        button_frame = tk.Frame(self.frame)
        button_frame.pack(fill=tk.X, expand=True)
        
        # Create all buttons
        buttons = [
            tk.Button(button_frame, text="New Game", command=self.new_game_command),
            tk.Button(button_frame, text="Check", command=self.check_command),
            tk.Button(button_frame, text="Solve", command=self.solve_command),
            tk.Button(button_frame, text="Stats", command=self.stats_command)
        ]
        
        # Place buttons with equal spacing but flush with edges
        num_buttons = len(buttons)
        for i, btn in enumerate(buttons):
            # Configure column weight for even spacing
            button_frame.columnconfigure(i, weight=1)
            
            # Set padx based on position:
            if i == 0:  # First button - no padding on left
                padx = (0, 5)
            elif i == num_buttons - 1:  # Last button - no padding on right
                padx = (5, 0)
            else:  # Middle buttons - padding on both sides
                padx = 5
                
            # Grid the button
            btn.grid(row=0, column=i, sticky="ew", padx=padx, pady=5)

    def grid(self, **kwargs):
        """Grid the control panel using the frame's grid method."""
        self.frame.grid(**kwargs)

class StatusFrame:
    """Frame to hold the status label."""

    def __init__(self, parent):
        """Initialize the status frame."""
        self.frame = tk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        self._create_widgets()

    def _create_widgets(self):
        """Create the widgets for the status frame."""
        self.status_label = tk.Label(
            self.frame,
            text="Ready!",
            anchor="w",
            padx=5,
            pady=3
        )
        self.status_label.pack(fill=tk.X)

    def game_over(self):
        """Update the status label to indicate game over."""
        self.status_label.config(text="Game Over!")
        
    def update_status(self, status: str):
        """Update the status label with the given text."""
        self.status_label.config(text=status)

class OptionsFrame:
    """Frame to hold difficulty selection options."""

    def __init__(self, parent, on_difficulty_change, difficulty, on_note_toggle):
        """Initialize the options frame."""
        self.frame = tk.Frame(parent, relief=tk.GROOVE, borderwidth=1)
        self.on_difficulty_change = on_difficulty_change
        self.difficulty = difficulty
        self.note_mode = tk.BooleanVar()  # Add note_mode attribute
        self.on_note_toggle = on_note_toggle
        self._create_widgets()

    def _create_widgets(self):
        """Create the widgets for the options frame."""
        self._create_difficulty_combobox()
        self._create_note_checkbutton()

    def _create_difficulty_combobox(self):
        """Create the difficulty combobox."""
        tk.Label(self.frame, text="Difficulty:").pack(side=tk.LEFT, padx=5, pady=5)
        difficulty_combo = ttk.Combobox(
            self.frame,
            textvariable=self.difficulty,
            values=[difficulty.value for difficulty in Difficulty],
            state="readonly",
            width=10
        )
        difficulty_combo.pack(side=tk.LEFT, padx=5, pady=5)
        difficulty_combo.bind("<<ComboboxSelected>>", self.on_difficulty_change)

    def _create_note_checkbutton(self):
        """Create the note checkbutton."""
        note_check = tk.Checkbutton(
            self.frame,
            text="Note Mode",
            variable=self.note_mode,
            command=self._toggle_note_mode
        )
        note_check.pack(side=tk.LEFT, padx=5, pady=5)

    def _toggle_note_mode(self):
        """Toggle note mode and call the callback."""
        self.on_note_toggle(self.note_mode.get())
