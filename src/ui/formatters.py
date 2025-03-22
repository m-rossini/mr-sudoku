from abc import ABC, abstractmethod
from typing import Dict, Any
from core.difficulty import Difficulty

class StatsFormatter(ABC):
    """Interface for formatting game statistics."""
    
    @abstractmethod
    def format_stats(self, difficulty: Difficulty, stats: Dict[str, Any]) -> str:
        """
        Format stats for display.
        
        Args:
            difficulty: The difficulty level
            stats: Dictionary of statistics
            
        Returns:
            Formatted stats as a string
        """
        pass


class BasicStatsFormatter(StatsFormatter):
    """Basic implementation of stats formatter that returns plain text."""
    
    def format_stats(self, difficulty: Difficulty, stats: Dict[str, Any]) -> str:
        """Format stats as plain text with labels."""
        from core.stats import GameStats  # Import here to avoid circular imports
        
        lines = [f"Statistics for {difficulty.value} difficulty:"]
        lines.append("-" * 30)
        
        # Games info
        lines.append(f"Games Played: {stats.get(GameStats.GAMES_PLAYED, 0)}")
        lines.append(f"Games Won: {stats.get(GameStats.GAMES_WON, 0)}")
        lines.append(f"Games Lost: {stats.get(GameStats.GAMES_LOST, 0)}")
        
        # Win rate
        played = stats.get(GameStats.GAMES_PLAYED, 0)
        won = stats.get(GameStats.GAMES_WON, 0)
        win_rate = (won / played * 100) if played > 0 else 0
        lines.append(f"Win Rate: {win_rate:.1f}%")
        
        lines.append("-" * 30)
        
        # Moves info
        lines.append(f"Total Moves: {stats.get(GameStats.TOTAL_MOVES, 0)}")
        lines.append(f"Wrong Moves: {stats.get(GameStats.WRONG_MOVES, 0)}")
        
        # Time info
        fastest = stats.get(GameStats.FASTEST_WIN_TIME, float('inf'))
        if fastest != float('inf'):
            lines.append(f"Fastest Win: {self._format_time(fastest)}")
            
        longest = stats.get(GameStats.LONGEST_WIN_TIME, 0)
        if longest > 0:
            lines.append(f"Longest Win: {self._format_time(longest)}")
        
        lines.append("-" * 30)
        
        # Streak info
        lines.append(f"Current Streak: {stats.get(GameStats.CURRENT_STREAK, 0)}")
        lines.append(f"Best Win Streak: {stats.get(GameStats.LONGEST_WIN_STREAK, 0)}")
        
        return "\n".join(lines)
    
    def _format_time(self, seconds: float) -> str:
        """Format time in seconds to a readable string."""
        minutes, secs = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"