from loguru import logger

import sys

# Remove default Loguru handler to avoid duplicate logs
logger.remove()

# Configure Loguru to log to console and file
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")


# Optional: Customize logging for third-party libraries
def intercept_loguru(record):
    # Convert Loguru log records to standard logging format
    return "{time} | {level} | {message}".format(**record)


# Make the logger accessible throughout your library
core_logger = logger
