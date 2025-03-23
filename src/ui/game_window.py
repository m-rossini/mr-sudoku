import tkinter as tk
from tkinter import ttk, messagebox
from core.difficulty import Difficulty
from core.stats import GameStats
from ui.ui_components import NumberPanel, StatsWindow, SudokuBoard, ControlPanel # Add ControlPanel import

INITIAL_STATUS = "Ready!"
class SudokuGameWindow:
    """Tkinter UI for the Sudoku game using individual tile objects."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the Sudoku game window."""
        self.root = root
        self.controller = None
        self.cell_size = 50
        self.margin = 20
        self.grid_size = 9
        self.difficulty = tk.StringVar(value="Medium")
        
        # UI state
        self.selected_cell = None
        
        # Register the window close event handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        self._setup_ui()
    
    def _setup_ui(self):
        """Create all UI components by calling specialized methods."""
        # Configure the root window
        window_size = 2 * self.margin + self.grid_size * self.cell_size
        self.root.geometry(f"{window_size}x{window_size + 200}") 
        self.root.resizable(False, False)
        
        # Create frames for different parts of the UI
        main_frame = self._create_main_frame()
        self._create_board(main_frame)
        self._create_number_panel(main_frame)
        self._create_options_frame(main_frame)
        self._create_controls_frame(main_frame)
        self._create_status_frame(main_frame)
        
        # Bind keyboard events for number input
        self.root.bind("<Key>", self._on_key_press)
    
    def _on_window_close(self):
        """Handle window close event."""
        # Ask user to confirm exit
        completed = self.controller.is_game_complete()
        if completed:
            msg = "Congratulations! You have completed the game"
            self.controller.update_stat(Difficulty(self.difficulty.get()), GameStats.GAMES_WON, 1)
        else:
            msg = "You did not complete the game"
            self.controller.update_stat(Difficulty(self.difficulty.get()), GameStats.GAMES_LOST, 1)

        if messagebox.askyesno("Quit", f"{msg}. Are you sure you want to quit? " ):
            if self.controller:
                self.controller.save_stats()
            
            self.root.destroy()
    
    def set_controller(self, controller):
        """Set the game controller after initialization."""
        self.controller = controller
        self.update_board()
    
    def _create_main_frame(self):
        """Create the main frame to hold the board."""
        main_frame = tk.Frame(self.root, padx=self.margin, pady=self.margin)
        main_frame.pack()
        return main_frame
 
    def _create_status_frame(self, main_frame):
        """Create the status frame with status label."""
        status_frame = tk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=1)
        status_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        
        self.status_label = tk.Label(
            status_frame, 
            text=INITIAL_STATUS, 
            anchor="w", 
            padx=5, 
            pady=3
        )
        self.status_label.pack(fill=tk.X)
        
        return status_frame
    
    def _create_board(self, main_frame):
        """Create the Sudoku board."""
        self.board = SudokuBoard(main_frame, self._on_cell_click)
        self.board.parent.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
    
    def _create_number_panel(self, main_frame):
        """Create the number panel below the Sudoku board."""
        self.number_panel = NumberPanel(main_frame, self._on_number_tile_click)
        self.number_panel.frame.grid(row=3, column=0, columnspan=3, pady=(10, 0), sticky="ew")
    
    def _create_options_frame(self, main_frame):
        """Create the options frame."""
        # Create frame with border
        options_frame = tk.Frame(main_frame, relief=tk.GROOVE, borderwidth=1)
        options_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0), sticky="ew")
        
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
        self.control_panel = ControlPanel(
            main_frame,
            new_game_command=self._new_game,
            check_command=self._check_solution,
            solve_command=self._solve_game,
            stats_command=self._show_stats
        )
        self.control_panel.grid(row=5, column=0, columnspan=3, pady=10, padx=0, sticky="ew")
    
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
        if not self.controller:
            print("No controller set for SudokuGameWindow")
            return 
        
        board = self.controller.get_board()
        self.board.update_board(board, self.selected_cell)
        self.update_number_panel()
    
    def _on_cell_click(self, row: int, col: int):
        """Handle cell click events."""
        # Update selection state
        self.selected_cell = (row, col)
        
        # Update the visual state of all tiles
        self._update_tile_appearances()

    def _update_tile_appearances(self):
        """Update the appearance of all tiles based on current game state."""
        board = self.controller.get_board()
        self.board.update_board(board, self.selected_cell)

    def _on_key_press(self, event):
        """Handle keyboard input."""
        if not self.selected_cell:
            return
        
        row, col = self.selected_cell
        
        if self.controller.is_fixed_cell(row, col):
            return
        
        # Number keys (1-9)
        if event.char.isdigit() and 1 <= int(event.char) <= 9:
            value = int(event.char)
            is_valid = self.controller.is_valid_move(row, col, value)
            
            if is_valid:
                self._handle_valid_move(row, col, value)
            else:
                self._handle_invalid_move(row, col, value)
        
        # Delete/backspace to clear a cell
        elif event.keysym in ('Delete', 'BackSpace'):
            self.controller.set_cell_value(row, col, 0)
            self.update_board()

    def _handle_valid_move(self, row: int, col: int, value: int):
        """Handle a valid move."""
        self.controller.set_cell_value(row, col, value)
        self.controller.update_stat(Difficulty(self.difficulty.get()), GameStats.TOTAL_MOVES, 1)
        self.update_number_panel()
    
    def _handle_invalid_move(self, row: int, col: int, value: int):
        """Handle an invalid move."""
        self.board.tiles[row][col].flash_invalid()
        is_game_over, wrong_moves, max_wrong_moves = self.controller.wrong_move_done()
        print(f'Invalid move: {value} at ({row},{col}), wrong_moves: {wrong_moves}/{max_wrong_moves}')
        self.controller.update_stat(Difficulty(self.difficulty.get()), GameStats.WRONG_MOVES, 1)
        self.update_status(f"Invalid: {value} at ({row+1},{col+1}) - Wrong Moves: {wrong_moves}/{max_wrong_moves}")
        self.update_number_panel()
        if is_game_over:
            self.__game_over()
    
    def __game_over(self):
        """Handle game over state."""
        self.update_status("Game Over")
        self.disable_grid()
        self.controller.update_stat(Difficulty(self.difficulty.get()), GameStats.GAMES_LOST, 1)
        self.controller.save_stats()
        
    def disable_grid(self):
        """Disable all tiles in the grid."""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.board.tiles[row][col].label.unbind("<Button-1>")
        self.root.unbind("<Key>")
    
    def enable_grid(self):
        """Enable all tiles in the grid."""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.board.tiles[row][col].label.bind("<Button-1>", self.board.tiles[row][col]._handle_click)
        self.root.bind("<Key>", self._on_key_press)
    
    def _new_game(self):
        """Start a new game with the selected difficulty."""
        difficulty = Difficulty(self.difficulty.get())
        self.controller.start_new_game(difficulty)
        self.enable_grid()
        self.update_status(INITIAL_STATUS)
        self.controller.update_stat(difficulty, GameStats.GAMES_PLAYED, 1)
        self.update_number_panel()
    
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
    
    def _on_number_tile_click(self, number: int):
        """Handle number tile click events."""
        if self.selected_cell:
            row, col = self.selected_cell
            if not self.controller.is_fixed_cell(row, col):
                is_valid = self.controller.is_valid_move(row, col, number)
                if is_valid:
                    self.controller.set_cell_value(row, col, number)
                    self.update_board()
    
    def update_number_panel(self):
        """Update the number panel with the current counts."""
        counts = [9] * 9
        board = self.controller.get_board()
        print(f'>>>board: {board}')
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                value = board[row][col]
                if value != 0:
                    counts[value-1] -= 1
        self.number_panel.update_counts(counts)
