import logging
import os
import sys
from datetime import datetime

class SystemLogger:
    def __init__(self, log_dir="logs", log_level=logging.INFO):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Setup python logging
        self.logger = logging.getLogger("ThothDaemon")
        self.logger.setLevel(log_level)
        self.logger.handlers = [] # Clear existing handlers

        # File Handler
        file_handler = logging.FileHandler(os.path.join(log_dir, "system.log"))
        file_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def info(self, source, message):
        self.logger.info(f"[{source}] {message}")

    def warning(self, source, message):
        self.logger.warning(f"[{source}] {message}")

    def error(self, source, message):
        self.logger.error(f"[{source}] {message}")

    def debug(self, source, message):
        self.logger.debug(f"[{source}] {message}")
