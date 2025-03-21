import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Tuple, Callable
from core.difficulty import Difficulty
from core.stats import GameStats
from ui.formatters import BasicStatsFormatter, StatsFormatter

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
        print("Tile clicked:", self.row, self.col)
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


INITIAL_STATUS = "Ready!"

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


class SudokuGameWindow:
    """Tkinter UI for the Sudoku game using individual tile objects."""
    
    def __init__(self, root: tk.Tk, game_model):#TODO Should I remove game_model from the constructor?
        self.root = root
        # self.game = game_model #TODO Do i really need the game model in the game window? Shouldn't be a controller concern? 
        self.controller = None
        self.cell_size = 50  # Size of each cell
        self.margin = 20
        self.grid_size = 9
        self.difficulty = tk.StringVar(value=Difficulty.MEDIUM.value)  # Default difficulty
        
        # UI state
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.tiles: List[List[SudokuTile]] = [[None for _ in range(9)] for _ in range(9)]
        
        self._setup_ui()
        # self.update_board() #TODO Given the controller is not set yet, this should not be called during initialization
    
    def set_controller(self, controller):
        """Set the controller for the game window."""
        self.controller = controller
    
    def _setup_ui(self):
        """Create all UI components by calling specialized methods."""
        # Configure the root window
        window_size = 2*self.margin + self.grid_size*self.cell_size
        self.root.geometry(f"{window_size}x{window_size+150}")  # Increased height for status
        self.root.resizable(False, False)
        
        # Create frames for different parts of the UI
        main_frame = self._create_main_frame()
        self._create_board(main_frame)
        self._create_options_frame(main_frame)
        self._create_controls_frame(main_frame)
        self._create_status_frame(main_frame)  # Add this line
        
        # Bind keyboard events for number input
        self.root.bind("<Key>", self._on_key_press)

    def _create_status_frame(self, main_frame):
        """Create the status frame with status label."""
        status_frame = tk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=1)
        status_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        
        self.status_label = tk.Label(
            status_frame, 
            text=INITIAL_STATUS,  # Define this constant at the top of your file
            anchor="w", 
            padx=5, 
            pady=3
        )
        self.status_label.pack(fill=tk.X)
        
        return status_frame
    
    def _create_main_frame(self):
        """Create the main frame to hold the board."""
        main_frame = tk.Frame(self.root, padx=self.margin, pady=self.margin)
        main_frame.pack()
        return main_frame
    
    def _create_board(self, main_frame):
        """Create the Sudoku board with boxes and tiles."""
        # Create 3x3 grid of box frames (each containing 3x3 cells)
        self.boxes = []
        for box_row in range(3):
            for box_col in range(3):
                # Create a frame for each 3x3 box with a visible border
                box = tk.Frame(
                    main_frame, 
                    borderwidth=2,
                    relief=tk.RAISED
                )
                box.grid(row=box_row, column=box_col, padx=1, pady=1)
                self.boxes.append(box)
                
                # Create 3x3 cells inside each box
                for cell_row in range(3):
                    for cell_col in range(3):
                        # Calculate the actual row and column in the full 9x9 grid
                        row = box_row * 3 + cell_row
                        col = box_col * 3 + cell_col
                        
                        # Create a tile and add it to our grid
                        tile = SudokuTile(
                            box, 
                            row, 
                            col, 
                            self.cell_size,
                            0,
                            self._on_cell_click
                        )
                        tile.grid(row=cell_row, column=cell_col)
                        
                        # Store the tile in our grid
                        self.tiles[row][col] = tile
    
    def _create_options_frame(self, main_frame):
        """Create the options frame."""
        # Create frame with border
        options_frame = tk.Frame(main_frame, relief=tk.GROOVE, borderwidth=1)
        options_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0), sticky="ew")
        
        # Add difficulty label and dropdown
        tk.Label(options_frame, text="Difficulty:").pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create the difficulty combobox
        difficulty_combo = ttk.Combobox(
            options_frame,
            textvariable=self.difficulty,
            values=[difficulty.value for difficulty in Difficulty],
            state="readonly",
            width=10
        )
        difficulty_combo.pack(side=tk.LEFT, padx=5, pady=5)
        difficulty_combo.bind("<<ComboboxSelected>>", self._on_difficulty_change)
    
    def _create_controls_frame(self, main_frame):
        """Create the game controls frame with buttons."""
        # Create controls frame
        controls_frame = tk.Frame(main_frame)
        controls_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky="ew")
        
        # Add control buttons
        new_game_btn = tk.Button(controls_frame, text="New Game", command=self._new_game)
        new_game_btn.pack(side=tk.LEFT, padx=5)
        
        check_btn = tk.Button(controls_frame, text="Check", command=self._check_solution)
        check_btn.pack(side=tk.LEFT, padx=5)
        
        solve_btn = tk.Button(controls_frame, text="Solve", command=self._solve_game)
        solve_btn.pack(side=tk.RIGHT, padx=5)
        
        stats_btn = tk.Button(controls_frame, text="Stats", command=self._show_stats)
        stats_btn.pack(side=tk.RIGHT, padx=5)
    
    def _show_stats(self):
        """Show a popup window with the game stats."""
        # Get current difficulty from the StringVar
        current_difficulty = Difficulty(self.difficulty.get())
        StatsWindow(self.root, self.controller, current_difficulty)
    
    def update_status(self, status: str):
        """Update the game status label."""
        self.status_label.config(text=f"{status}")
    
    def update_board(self):
        """Update the UI to reflect the current game state."""
        # board = game.get_board()  # Use getter method instead of direct attribute access
        board = self.controller.get_board()
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                value = board[row][col]
                is_fixed = self.controller.is_fixed_cell(row, col)
                is_selected = self.selected_cell == (row, col)
                
                # Update the tile
                self.tiles[row][col].set_value(value, is_fixed)
                self.tiles[row][col].set_selected(is_selected)
    
    def _on_cell_click(self, row: int, col: int):
        """Handle cell click events."""
        self.selected_cell = (row, col)
        # Just update the selected status without reloading the entire board
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                self.tiles[r][c].set_selected((r, c) == self.selected_cell)
    
    def _on_key_press(self, event):
        """Handle keyboard input."""
        if not self.selected_cell:
            return
        
        row, col = self.selected_cell
        
        if self.controller.is_fixed_cell(row, col):
            return
        
        if event.char.isdigit() and 1 <= int(event.char) <= 9:
            is_valid = self.controller.is_valid_move(row, col, int(event.char))
            
            if is_valid:
                value = int(event.char)
                self.controller.set_cell_value(row, col, value)
                self.controller.update_stat(Difficulty(self.difficulty.get()), GameStats.TOTAL_MOVES, 1)
            else:
                self.tiles[row][col].flash_invalid()
                is_game_over, wrong_moves, max_wrong_moves = self.controller.wrong_move_done()
                print(f'wrong_moves: {wrong_moves}, max_wrong_moves: {max_wrong_moves}, is_game_over: {is_game_over}')
                self.controller.update_stat(Difficulty(self.difficulty.get()), GameStats.WRONG_MOVES, wrong_moves)
                self.update_status(f"Wrong Moves: {wrong_moves}/{max_wrong_moves}")
                if is_game_over:
                    self.update_status("Game Over")
                    self.disable_grid()
                    self.controller.update_stat(Difficulty(self.difficulty.get()), GameStats.GAMES_LOST, 1)
        
        elif event.keysym in ('Delete', 'BackSpace'):
            self.controller.set_cell_value(row, col, 0)
    
    def disable_grid(self):
        """Disable all tiles in the grid."""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.tiles[row][col].label.unbind("<Button-1>")
        self.root.unbind("<Key>")
    
    def enable_grid(self):
        """Enable all tiles in the grid."""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.tiles[row][col].label.bind("<Button-1>", self.tiles[row][col]._handle_click)
        self.root.bind("<Key>", self._on_key_press)
    
    def _new_game(self):
        """Start a new game with the selected difficulty."""
        difficulty = Difficulty(self.difficulty.get())
        self.controller.start_new_game(difficulty)
        self.enable_grid()
        self.update_status(INITIAL_STATUS)
        self.controller.update_stat(difficulty, GameStats.GAMES_PLAYED, 1)
    
    def _check_solution(self):
        """Check if the current board state is valid."""
        self.controller.check_solution()
    
    def _solve_game(self):
        """Request the game model to solve the puzzle."""
        self.controller.solve_game()
    
    def _on_difficulty_change(self, event):
        """Handle difficulty selection changes."""
        new_difficulty = Difficulty(self.difficulty.get())
        if messagebox.askyesno("New Game", f"Start a new {new_difficulty.value} game?"):
            self.controller.start_new_game(new_difficulty)
            self.enable_grid()
    
    def show_message(self, title: str, message: str):
        """Show a message box with the given title and message."""
        messagebox.showinfo(title, message)