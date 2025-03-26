import json
import os
from typing import Dict, Any
from core.difficulty import Difficulty

class GameStats:
    """Class to track game statistics."""
    
    # Stats keys
    GAMES_PLAYED = "games_played"
    GAMES_WON = "games_won"
    GAMES_LOST = "games_lost"
    TOTAL_MOVES = "total_moves"
    WRONG_MOVES = "wrong_moves"
    FASTEST_WIN_TIME = "fastest_win_time"
    LONGEST_WIN_TIME = "longest_win_time"
    CURRENT_STREAK = "current_streak"
    LONGEST_WIN_STREAK = "longest_win_streak"
    LONGEST_LOSS_STREAK = "longest_loss_streak"
    
    # Default filename for stats
    DEFAULT_FILENAME = "sudoku_stats.json"
    
    # Default values for stats
    DEFAULT_VALUES = {
        GAMES_PLAYED: 0,
        GAMES_WON: 0,
        GAMES_LOST: 0,
        TOTAL_MOVES: 0,
        WRONG_MOVES: 0,
        FASTEST_WIN_TIME: float('inf'),
        LONGEST_WIN_TIME: 0,
        CURRENT_STREAK: 0,
        LONGEST_WIN_STREAK: 0,
        LONGEST_LOSS_STREAK: 0
    }
    
    def __init__(self):
        """Initialize the game statistics."""
        self.stats=self.load_stats()
    
    @classmethod
    def get_default_stats(cls):
        """Get a copy of the default stats dictionary."""
        return cls.DEFAULT_VALUES.copy()
    
    def update_stats(self, difficulty: Difficulty, won: bool, moves: int, wrong_moves: int, time_taken: float):
        """Update the stats for the given difficulty level."""
        stats = self.stats[difficulty]
        stats[self.TOTAL_MOVES] += moves
        stats[self.WRONG_MOVES] += wrong_moves
        if won:
            stats[self.GAMES_WON] += 1
            stats[self.CURRENT_STREAK] = max(0, stats[self.CURRENT_STREAK]) + 1
            stats[self.LONGEST_WIN_STREAK] = max(stats[self.LONGEST_WIN_STREAK], stats[self.CURRENT_STREAK])
            stats[self.FASTEST_WIN_TIME] = min(stats[self.FASTEST_WIN_TIME], time_taken)
            stats[self.LONGEST_WIN_TIME] = max(stats[self.LONGEST_WIN_TIME], time_taken)
        else:
            stats[self.GAMES_LOST] += 1
            stats[self.CURRENT_STREAK] = min(0, stats[self.CURRENT_STREAK]) - 1
            stats[self.LONGEST_LOSS_STREAK] = min(stats[self.LONGEST_LOSS_STREAK], stats[self.CURRENT_STREAK])
    
    def get_stats(self, difficulty: Difficulty) -> dict[str, int]:
        """Return the stats for the given difficulty level."""
        return self.stats[difficulty]
    
    def save_stats(self, filename: str = DEFAULT_FILENAME) -> bool:
        """Save the stats to a file."""
        try:
            # Convert Difficulty enum keys to strings for JSON serialization
            serializable_stats = {diff.value: stats for diff, stats in self.stats.items()}
            
            with open(filename, 'w') as f:
                json.dump(serializable_stats, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving stats: {e}")
            return False
    
    def load_stats(self, filename: str = DEFAULT_FILENAME) -> bool:
        """
        Load stats from a file if it exists, or create default stats file.
        Returns True if successful, False otherwise.
        """
        if not os.path.exists(filename):
            print(f"Stats file {filename} not found. Creating default stats file.")
            # Initialize with default values
            stats = {difficulty: self.get_default_stats() for difficulty in Difficulty}
            return stats
        
        try:
            with open(filename, 'r') as f:
                loaded_data = json.load(f)
            
            # Convert string difficulty keys back to enum
            stats_data = {}
            for diff_str, stats in loaded_data.items():
                try:
                    diff = next((d for d in Difficulty if d.value == diff_str), None)
                    if diff:
                        stats_data[diff] = stats
                except Exception:
                    print(f"Unknown difficulty: {diff_str}")
            
            # Check compatibility and merge with defaults
            self._merge_stats(stats_data)
            return stats_data
        except Exception as e:
            print(f"Error loading stats: {e}")
            # If error occurs during loading, create new default file
            print("Creating new default stats file.")
            default_stats = self.create_default_stats_for_all_difficulties()
            self.save_stats(default_stats, filename)
            return default_stats  # Return default stats since we now have valid stats
    
    @classmethod
    def _merge_stats(cls, loaded_stats: Dict[Difficulty, Dict[str, Any]]):
        """
        Merge loaded stats with default values, ensuring compatibility.
        """
        for difficulty in Difficulty:
            if difficulty in loaded_stats:
                loaded_diff_stats = loaded_stats[difficulty]
                
                # Start with default values to ensure all required stats exist
                merged_stats = cls.get_default_stats()
                
                # Override with values from loaded stats if they exist
                for stat_key in cls.get_default_stats().keys():
                    if stat_key in loaded_diff_stats:
                        merged_stats[stat_key] = loaded_diff_stats[stat_key]
                
                # Update stats for this difficulty
                loaded_stats[difficulty] = merged_stats
