import logging
import os
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self, name="ApplicationLogger", log_file="app.log", level=logging.INFO, max_size=2*1024*1024, backup_count=10):
        """
        Initializes the Logger with a specified name, log file, and logging level.
        
        Parameters:
        - name (str): Name for the logger.
        - log_file (str): Path to the log file.
        - level (logging level): Logging level (e.g., logging.DEBUG, logging.INFO).
        """
        try:
            self.logger = logging.getLogger(name)
            self.logger.setLevel(level)

            # Check only this logger's own handlers to avoid being affected by ancestor handlers
            if not self.logger.handlers:
                # Console handler for terminal output
                console_handler = logging.StreamHandler()
                console_handler.setLevel(level)
                self.logger.addHandler(console_handler)
                # Ensure log directory exists
                os.makedirs(os.path.dirname(log_file), exist_ok=True)

                # Add Rotating File Handler
                file_handler = RotatingFileHandler(log_file,maxBytes=max_size,backupCount=backup_count,encoding='utf-8',delay=True)
                file_handler.setLevel(level)
                self.logger.addHandler(file_handler)

                # Create a formatter with the format we want
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                for handler in self.logger.handlers:
                    handler.setFormatter(formatter)
        except Exception as e:
            logging.error("Error initializing logger:{}".format(e))
            raise ValueError("Error initializing logger:{}".format(e))

    def debug(self, *args,**kwargs):
        """Logs a debug message with multiple arguments."""
        try:
            self.logger.debug(" ".join(map(str, args)), **kwargs)
        except Exception as e:
            logging.error("Error logging debug message:{}".format(e))
            raise ValueError("Error logging debug message:{}".format(e))

    def info(self, *args,**kwargs):
        """Logs an informational message with multiple arguments."""
        try:    
            self.logger.info(" ".join(map(str, args)), **kwargs)
        except Exception as e:
            logging.error("Error logging info message:{}".format(e))
            raise ValueError("Error logging info message:{}".format(e))

    def warning(self, *args,**kwargs):
        """Logs a warning message with multiple arguments."""
        try:    
            self.logger.warning(" ".join(map(str, args)), **kwargs)
        except Exception as e:
            logging.error("Error logging warning message:{}".format(e))
            raise ValueError("Error logging warning message:{}".format(e))

    def error(self, *args: object,**kwargs) -> object:
        """Logs an error message with multiple arguments."""
        try:    
            self.logger.error(" ".join(map(str, args)), **kwargs)
        except Exception as e:
            logging.error("Error logging error message:{}".format(e))
            raise ValueError("Error logging error message:{}".format(e))

    def critical(self, *args,**kwargs):
        """Logs a critical message with multiple arguments."""
        try:    
            self.logger.critical(" ".join(map(str, args)), **kwargs)
        except Exception as e:
            logging.error("Error logging critical message:{}".format(e))
            raise ValueError("Error logging critical message:{}".format(e))

    def close_handlers(self):
        """Method to close and cleanup handlers (e.g., on app shutdown)."""
        try:
            for handler in self.logger.handlers:
                handler.close()
                self.logger.removeHandler(handler)
        except Exception as e:
            logging.error("Error closing logger handlers:{}".format(e))
            raise ValueError("Error closing logger handlers:{}".format(e))
