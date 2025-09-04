"""
Background task system for periodic notification monitoring.
Integrates with the existing scheduler to run fantasy-specific monitoring tasks.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import threading
import time

from ..database.connection import get_db
from .notification_service import FantasyNotificationService
from .service import create_notification_service
from ..platforms.service import PlatformIntegrationService
from ..news.service import NewsAggregationService

logger = logging.getLogger(__name__)


class NotificationBackgroundTasks:
    """
    Background task system for automated notification monitoring.
    """
    
    def __init__(self, fantasy_notification_service: FantasyNotificationService = None):
        """
        Initialize the background task system.
        
        Args:
            fantasy_notification_service: Fantasy notification service instance
        """
        self.fantasy_notification_service = fantasy_notification_service
        self.running = False
        self.task_threads = {}
        self.last_run_times = {}
        
        # Task configuration (intervals in minutes)
        self.task_config = {
            "roster_monitoring": {"interval": 30, "enabled": True},  # Every 30 minutes
            "injury_monitoring": {"interval": 15, "enabled": True},  # Every 15 minutes
            "news_monitoring": {"interval": 15, "enabled": True},    # Every 15 minutes
            "waiver_monitoring": {"interval": 60, "enabled": True},  # Every hour
            "cleanup_old_notifications": {"interval": 1440, "enabled": True}  # Daily
        }
    
    def start(self):
        """Start all background monitoring tasks."""
        if self.running:
            logger.warning("Background tasks already running")
            return
        
        logger.info("Starting notification background tasks...")
        self.running = True
        
        # Start each enabled task in its own thread
        for task_name, config in self.task_config.items():
            if config["enabled"]:
                thread = threading.Thread(
                    target=self._run_task_loop,
                    args=(task_name, config["interval"]),
                    name=f"NotificationTask-{task_name}"
                )
                thread.daemon = True
                thread.start()
                self.task_threads[task_name] = thread
                logger.info(f"Started background task: {task_name} (interval: {config['interval']} min)")
        
        logger.info(f"Started {len(self.task_threads)} notification background tasks")
    
    def stop(self):
        """Stop all background monitoring tasks."""
        logger.info("Stopping notification background tasks...")
        self.running = False
        
        # Wait for all threads to finish (with timeout)
        for task_name, thread in self.task_threads.items():
            if thread.is_alive():
                thread.join(timeout=30)
                if thread.is_alive():
                    logger.warning(f"Task {task_name} did not stop gracefully")
                else:
                    logger.debug(f"Stopped task: {task_name}")
        
        self.task_threads.clear()
        logger.info("All notification background tasks stopped")
    
    def _run_task_loop(self, task_name: str, interval_minutes: int):
        """
        Run a specific task in a loop with the specified interval.
        
        Args:
            task_name: Name of the task to run
            interval_minutes: Interval between runs in minutes
        """
        logger.info(f"Starting task loop for {task_name}")
        
        while self.running:
            try:
                start_time = time.time()
                
                # Run the task
                result = self._execute_task(task_name)
                
                # Track last run time
                self.last_run_times[task_name] = datetime.utcnow()
                
                execution_time = time.time() - start_time
                logger.debug(f"Task {task_name} completed in {execution_time:.2f}s: {result}")
                
                # Sleep for the remaining interval time
                sleep_time = (interval_minutes * 60) - execution_time
                if sleep_time > 0:
                    # Sleep in small chunks to allow for quick shutdown
                    while sleep_time > 0 and self.running:
                        chunk_sleep = min(sleep_time, 10)  # Sleep in 10-second chunks
                        time.sleep(chunk_sleep)
                        sleep_time -= chunk_sleep
                
            except Exception as e:
                logger.error(f"Error in task {task_name}: {e}")
                if self.running:  # Only sleep if we're still supposed to be running
                    time.sleep(60)  # Wait 1 minute before retrying
        
        logger.info(f"Task loop for {task_name} stopped")
    
    def _execute_task(self, task_name: str) -> Dict[str, Any]:
        """
        Execute a specific background task.
        
        Args:
            task_name: Name of the task to execute
            
        Returns:
            Dict containing task execution results
        """
        try:
            if task_name == "roster_monitoring":
                return self._run_roster_monitoring()
            elif task_name == "injury_monitoring":
                return self._run_injury_monitoring()
            elif task_name == "news_monitoring":
                return self._run_news_monitoring()
            elif task_name == "waiver_monitoring":
                return self._run_waiver_monitoring()
            elif task_name == "cleanup_old_notifications":
                return self._cleanup_old_notifications()
            else:
                return {"status": "error", "message": f"Unknown task: {task_name}"}
                
        except Exception as e:
            logger.error(f"Error executing task {task_name}: {e}")
            return {"status": "error", "message": str(e)}
    
    def _run_roster_monitoring(self) -> Dict[str, Any]:
        """
        Run comprehensive roster monitoring for all users.
        
        Returns:
            Dict containing monitoring results
        """
        logger.debug("Running roster monitoring task")
        
        if not self.fantasy_notification_service:
            return {"status": "skipped", "message": "Fantasy notification service not available"}
        
        try:
            with next(get_db()) as db:
                result = self.fantasy_notification_service.monitor_all_users(db)
                return result
                
        except Exception as e:
            logger.error(f"Error in roster monitoring: {e}")
            return {"status": "error", "message": str(e)}
    
    def _run_injury_monitoring(self) -> Dict[str, Any]:
        """
        Focus specifically on injury status monitoring.
        
        Returns:
            Dict containing injury monitoring results
        """
        logger.debug("Running injury monitoring task")
        
        # This would integrate with ESPN API to check for injury updates
        # For now, we'll log that we checked
        try:
            # In a real implementation, this would:
            # 1. Fetch latest player injury data from ESPN/other sources
            # 2. Compare against cached injury statuses
            # 3. Send notifications for status changes
            # 4. Update the injury cache
            
            monitored_count = 0
            notifications_sent = 0
            
            return {
                "status": "completed",
                "players_monitored": monitored_count,
                "notifications_sent": notifications_sent,
                "message": "Injury monitoring completed (mock implementation)"
            }
            
        except Exception as e:
            logger.error(f"Error in injury monitoring: {e}")
            return {"status": "error", "message": str(e)}
    
    def _run_news_monitoring(self) -> Dict[str, Any]:
        """
        Monitor breaking news that affects fantasy players.
        
        Returns:
            Dict containing news monitoring results
        """
        logger.debug("Running news monitoring task")
        
        try:
            # This would integrate with news services to check for breaking news
            # For now, we'll log that we checked
            
            news_items_checked = 0
            high_urgency_found = 0
            notifications_sent = 0
            
            return {
                "status": "completed",
                "news_items_checked": news_items_checked,
                "high_urgency_found": high_urgency_found,
                "notifications_sent": notifications_sent,
                "message": "News monitoring completed (mock implementation)"
            }
            
        except Exception as e:
            logger.error(f"Error in news monitoring: {e}")
            return {"status": "error", "message": str(e)}
    
    def _run_waiver_monitoring(self) -> Dict[str, Any]:
        """
        Monitor waiver wire for valuable pickup opportunities.
        
        Returns:
            Dict containing waiver monitoring results
        """
        logger.debug("Running waiver monitoring task")
        
        try:
            # This would check waiver wires for high-value pickups
            # For now, we'll log that we checked
            
            leagues_checked = 0
            opportunities_found = 0
            notifications_sent = 0
            
            return {
                "status": "completed",
                "leagues_checked": leagues_checked,
                "opportunities_found": opportunities_found,
                "notifications_sent": notifications_sent,
                "message": "Waiver monitoring completed (mock implementation)"
            }
            
        except Exception as e:
            logger.error(f"Error in waiver monitoring: {e}")
            return {"status": "error", "message": str(e)}
    
    def _cleanup_old_notifications(self) -> Dict[str, Any]:
        """
        Clean up old notifications to keep the database tidy.
        
        Returns:
            Dict containing cleanup results
        """
        logger.debug("Running notification cleanup task")
        
        try:
            with next(get_db()) as db:
                # Delete notifications older than 30 days
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                
                from ..database.models import Notification
                
                # Count old notifications before deleting
                old_notifications = db.query(Notification).filter(
                    Notification.created_at < cutoff_date
                ).count()
                
                # Delete old notifications
                deleted_count = db.query(Notification).filter(
                    Notification.created_at < cutoff_date
                ).delete()
                
                db.commit()
                
                logger.info(f"Cleaned up {deleted_count} old notifications")
                
                return {
                    "status": "completed",
                    "old_notifications_found": old_notifications,
                    "notifications_deleted": deleted_count,
                    "cutoff_date": cutoff_date.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error in notification cleanup: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_task_status(self) -> Dict[str, Any]:
        """
        Get the status of all background tasks.
        
        Returns:
            Dict containing status of all tasks
        """
        status = {
            "running": self.running,
            "active_tasks": len(self.task_threads),
            "tasks": {}
        }
        
        for task_name, config in self.task_config.items():
            task_status = {
                "enabled": config["enabled"],
                "interval_minutes": config["interval"],
                "thread_alive": self.task_threads.get(task_name, {}).is_alive() if task_name in self.task_threads else False,
                "last_run": self.last_run_times.get(task_name, {}).isoformat() if task_name in self.last_run_times else None
            }
            status["tasks"][task_name] = task_status
        
        return status
    
    def trigger_task(self, task_name: str) -> Dict[str, Any]:
        """
        Manually trigger a specific task (for testing/debugging).
        
        Args:
            task_name: Name of the task to trigger
            
        Returns:
            Dict containing task execution result
        """
        if task_name not in self.task_config:
            return {"status": "error", "message": f"Unknown task: {task_name}"}
        
        logger.info(f"Manually triggering task: {task_name}")
        result = self._execute_task(task_name)
        self.last_run_times[task_name] = datetime.utcnow()
        
        return result
    
    def update_task_config(self, task_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update configuration for a specific task.
        
        Args:
            task_name: Name of the task to update
            config: New configuration parameters
            
        Returns:
            Dict containing update result
        """
        if task_name not in self.task_config:
            return {"status": "error", "message": f"Unknown task: {task_name}"}
        
        old_config = self.task_config[task_name].copy()
        self.task_config[task_name].update(config)
        
        logger.info(f"Updated task {task_name} config: {old_config} -> {self.task_config[task_name]}")
        
        return {
            "status": "success",
            "task_name": task_name,
            "old_config": old_config,
            "new_config": self.task_config[task_name]
        }


# Global background task instance
notification_background_tasks = None


def initialize_background_tasks(fantasy_notification_service: FantasyNotificationService):
    """
    Initialize the global background task system.
    
    Args:
        fantasy_notification_service: Fantasy notification service instance
    """
    global notification_background_tasks
    
    if notification_background_tasks is None:
        notification_background_tasks = NotificationBackgroundTasks(fantasy_notification_service)
        logger.info("Notification background task system initialized")
    

def start_background_tasks():
    """Start the background task system."""
    global notification_background_tasks
    
    if notification_background_tasks is None:
        logger.error("Background task system not initialized. Call initialize_background_tasks first.")
        return False
    
    notification_background_tasks.start()
    return True


def stop_background_tasks():
    """Stop the background task system."""
    global notification_background_tasks
    
    if notification_background_tasks is not None:
        notification_background_tasks.stop()


def get_background_task_status() -> Dict[str, Any]:
    """Get status of background tasks."""
    global notification_background_tasks
    
    if notification_background_tasks is None:
        return {"status": "not_initialized"}
    
    return notification_background_tasks.get_task_status()


def trigger_background_task(task_name: str) -> Dict[str, Any]:
    """Manually trigger a background task."""
    global notification_background_tasks
    
    if notification_background_tasks is None:
        return {"status": "error", "message": "Background task system not initialized"}
    
    return notification_background_tasks.trigger_task(task_name)