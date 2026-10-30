# File: logger_config.py

import logging

def setup_logger(log_file: str = "app.log"):
    """
    Configure the logger to write to the specified log file.

    Args:
        log_file (str): Path to the log file.
    """
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,  # Capture all log levels
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
        filemode='a'  # Append to the log file
    )
    logging.getLogger().addHandler(logging.StreamHandler())  # Optional: Log to console as well
