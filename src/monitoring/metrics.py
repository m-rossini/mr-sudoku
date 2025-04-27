import logging
import time
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Configure logger
logger = logging.getLogger(__name__)

class MetricsService:
    """
    Service to handle Prometheus metrics for the Sudoku game.
    Follows the single responsibility principle by focusing solely on metrics collection.
    """
    
    def __init__(self, port=8000):
        """
        Initialize the metrics service with Prometheus metrics.
        
        Args:
            port: HTTP port to expose metrics on
        """
        logger.debug("> MetricsService::__init__ - Initializing Prometheus metrics service")
        self.port = port
        
        # Game lifecycle metrics
        self.game_starts = Counter('sudoku_game_starts_total', 'Total number of games started')
        self.game_exits = Counter('sudoku_game_exits_total', 'Total number of games exited')
        
        # Button clicks metrics
        self.button_clicks = Counter('sudoku_button_clicks_total', 'Total button clicks', ['button_name'])
        
        # Game play metrics
        self.moves_total = Counter('sudoku_moves_total', 'Total number of moves made')
        self.wrong_moves_total = Counter('sudoku_wrong_moves_total', 'Total number of wrong moves made')
        
        # Game time metrics (in seconds)
        self.game_time = Histogram(
            'sudoku_game_time_seconds', 
            'Time spent in game',
            buckets=[60, 120, 300, 600, 900, 1800, 3600]  # 1m, 2m, 5m, 10m, 15m, 30m, 1h
        )
        self.active_games = Gauge('sudoku_active_games', 'Number of active games')
        
        # Dictionary to track start times of active games
        self._game_start_times = {}
        
    def start_metrics_server(self):
        """Start the Prometheus metrics HTTP server."""
        logger.info(">> MetricsService::start_metrics_server - Starting Prometheus metrics server on port %s", self.port)
        start_http_server(self.port)
        
    def record_game_start(self, game_id):
        """
        Record a game start event.
        
        Args:
            game_id: Unique identifier for the game
        """
        logger.debug("> MetricsService::record_game_start - Recording game start for ID %s", game_id)
        self.game_starts.inc()
        self.active_games.inc()
        self._game_start_times[game_id] = time.time()
    
    def record_game_exit(self, game_id):
        """
        Record a game exit event.
        
        Args:
            game_id: Unique identifier for the game
        """
        logger.debug("> MetricsService::record_game_exit - Recording game exit for ID %s", game_id)
        self.game_exits.inc()
        self.active_games.dec()
        
        # Record game time if we have a start time
        if game_id in self._game_start_times:
            game_time = time.time() - self._game_start_times[game_id]
            self.game_time.observe(game_time)
            del self._game_start_times[game_id]
            logger.debug("> MetricsService::record_game_exit - Recorded game time of %.2f seconds", game_time)
    
    def record_button_click(self, button_name):
        """
        Record a button click event.
        
        Args:
            button_name: Name of the button clicked
        """
        logger.debug("> MetricsService::record_button_click - Recording click on button %s", button_name)
        self.button_clicks.labels(button_name=button_name).inc()
    
    def record_move(self):
        """Record a move made in the game."""
        logger.debug("> MetricsService::record_move - Recording game move")
        self.moves_total.inc()
    
    def record_wrong_move(self):
        """Record a wrong move made in the game."""
        logger.debug("> MetricsService::record_wrong_move - Recording wrong game move")
        self.wrong_moves_total.inc()


# Singleton instance for the application to use
metrics_service = None

def initialize_metrics(port=8000):
    """
    Initialize the metrics service and start the HTTP server.
    
    Args:
        port: HTTP port to expose metrics on
    
    Returns:
        The metrics service instance
    """
    global metrics_service
    if metrics_service is None:
        logger.info(">> MetricsService::initialize_metrics - Initializing Prometheus metrics on port %s", port)
        metrics_service = MetricsService(port)
        metrics_service.start_metrics_server()
    return metrics_service

def get_metrics_service():
    """
    Get the metrics service instance.
    
    Returns:
        The metrics service instance or None if not initialized
    """
    global metrics_service
    if metrics_service is None:
        logger.warning(">>> MetricsService::get_metrics_service - Metrics service not initialized")
    return metrics_service