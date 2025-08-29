import logging
import time
import psutil
import redis
from datetime import datetime
from typing import Dict, Any, Optional
import json

class MonitoringService:
    """
    Application monitoring service for Fantasy Football Domination App.
    Tracks performance metrics, errors, and system health.
    """
    
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379, 
                 log_level: str = 'INFO'):
        """
        Initialize monitoring service.
        
        Args:
            redis_host (str): Redis host for storing metrics
            redis_port (int): Redis port
            log_level (str): Logging level
        """
        # Set up logging
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('app.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('MonitoringService')
        
        # Set up Redis connection for metrics storage
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=1, decode_responses=True)
        
        # Performance tracking
        self.start_time = None
        self.operation_name = None
        
    def start_operation_tracking(self, operation_name: str) -> None:
        """
        Start tracking an operation's performance.
        
        Args:
            operation_name (str): Name of the operation to track
        """
        self.start_time = time.time()
        self.operation_name = operation_name
        self.logger.info(f"Starting operation: {operation_name}")
        
    def end_operation_tracking(self) -> Dict[str, Any]:
        """
        End tracking an operation's performance and log metrics.
        
        Returns:
            dict: Performance metrics
        """
        if not self.start_time or not self.operation_name:
            self.logger.warning("No operation tracking in progress")
            return {}
            
        end_time = time.time()
        duration = end_time - self.start_time
        
        # Collect system metrics
        cpu_percent = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        memory_percent = memory_info.percent
        
        metrics = {
            'operation_name': self.operation_name,
            'duration_seconds': duration,
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'timestamp': datetime.now().isoformat()
        }
        
        # Log metrics
        self.logger.info(f"Operation {self.operation_name} completed in {duration:.2f} seconds")
        self.logger.info(f"System metrics - CPU: {cpu_percent}%, Memory: {memory_percent}%")
        
        # Store metrics in Redis
        self._store_metrics(metrics)
        
        # Reset tracking
        self.start_time = None
        self.operation_name = None
        
        return metrics
        
    def _store_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Store metrics in Redis.
        
        Args:
            metrics (dict): Metrics to store
        """
        try:
            key = f"metrics:{metrics['operation_name']}:{datetime.now().strftime('%Y-%m-%d')}"
            self.redis_client.lpush(key, json.dumps(metrics))
            
            # Keep only last 100 metrics entries per operation per day
            self.redis_client.ltrim(key, 0, 99)
        except Exception as e:
            self.logger.error(f"Failed to store metrics in Redis: {str(e)}")
            
    def log_error(self, operation_name: str, error_message: str, 
                  error_details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error with details.
        
        Args:
            operation_name (str): Name of the operation where error occurred
            error_message (str): Error message
            error_details (dict, optional): Additional error details
        """
        error_info = {
            'operation_name': operation_name,
            'error_message': error_message,
            'error_details': error_details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.error(f"Error in {operation_name}: {error_message}")
        if error_details:
            self.logger.error(f"Error details: {json.dumps(error_details)}")
            
        # Store error in Redis
        try:
            key = f"errors:{operation_name}:{datetime.now().strftime('%Y-%m-%d')}"
            self.redis_client.lpush(key, json.dumps(error_info))
            
            # Keep only last 50 errors per operation per day
            self.redis_client.ltrim(key, 0, 49)
        except Exception as e:
            self.logger.error(f"Failed to store error in Redis: {str(e)}")
            
    def log_warning(self, operation_name: str, warning_message: str,
                    warning_details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a warning with details.
        
        Args:
            operation_name (str): Name of the operation where warning occurred
            warning_message (str): Warning message
            warning_details (dict, optional): Additional warning details
        """
        warning_info = {
            'operation_name': operation_name,
            'warning_message': warning_message,
            'warning_details': warning_details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.warning(f"Warning in {operation_name}: {warning_message}")
        if warning_details:
            self.logger.warning(f"Warning details: {json.dumps(warning_details)}")
            
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get current system metrics.
        
        Returns:
            dict: Current system metrics
        """
        cpu_percent = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu_percent,
            'memory_total': memory_info.total,
            'memory_available': memory_info.available,
            'memory_percent': memory_info.percent,
            'disk_total': disk_info.total,
            'disk_used': disk_info.used,
            'disk_free': disk_info.free,
            'disk_percent': (disk_info.used / disk_info.total) * 100,
            'timestamp': datetime.now().isoformat()
        }
        
    def get_operation_metrics(self, operation_name: str, limit: int = 10) -> list:
        """
        Get recent metrics for a specific operation.
        
        Args:
            operation_name (str): Name of the operation
            limit (int): Number of recent metrics to retrieve
            
        Returns:
            list: Recent metrics for the operation
        """
        try:
            key = f"metrics:{operation_name}:{datetime.now().strftime('%Y-%m-%d')}"
            metrics_list = self.redis_client.lrange(key, 0, limit - 1)
            return [json.loads(metric) for metric in metrics_list]
        except Exception as e:
            self.logger.error(f"Failed to retrieve operation metrics: {str(e)}")
            return []
            
    def check_system_health(self) -> Dict[str, Any]:
        """
        Check overall system health and return status.
        
        Returns:
            dict: System health status
        """
        metrics = self.get_system_metrics()
        
        # Define health thresholds
        cpu_threshold = 80  # % CPU usage
        memory_threshold = 85  # % memory usage
        disk_threshold = 90  # % disk usage
        
        # Determine health status
        status = "HEALTHY"
        alerts = []
        
        if metrics['cpu_percent'] > cpu_threshold:
            status = "WARNING"
            alerts.append(f"High CPU usage: {metrics['cpu_percent']}%")
            
        if metrics['memory_percent'] > memory_threshold:
            status = "WARNING"
            alerts.append(f"High memory usage: {metrics['memory_percent']}%")
            
        if metrics['disk_percent'] > disk_threshold:
            status = "WARNING"
            alerts.append(f"High disk usage: {metrics['disk_percent']}%")
            
        return {
            'status': status,
            'metrics': metrics,
            'alerts': alerts,
            'timestamp': datetime.now().isoformat()
        }

# Example usage:
# monitoring_service = MonitoringService()
# 
# # Track an operation
# monitoring_service.start_operation_tracking("fetch_player_data")
# # ... perform operation ...
# metrics = monitoring_service.end_operation_tracking()
# 
# # Log an error
# monitoring_service.log_error("fetch_player_data", "Failed to connect to database", 
#                             {"player_id": "12345", "error_code": 500})
# 
# # Check system health
# health = monitoring_service.check_system_health()
# print(health)
