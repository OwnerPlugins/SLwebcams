#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import inspect
import traceback
from datetime import datetime

# Force log writing to plugin directory
PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(PLUGIN_DIR, "logs")
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
LOG_FILE = os.path.join(LOGS_DIR, "sl_logs.txt")

# Maximum log file size (1MB)
MAX_LOG_SIZE = 1024 * 1024


class SLLogger:
    """
    Advanced logger for the SLwebcams plugin.
    Handles creation, rotation and writing of logs with detailed information.
    """

    @staticmethod
    def initialize():
        """
        Initialize the log file, deleting the previous one if it exists.
        Called at plugin startup.
        """
        try:
            # Create the directory if it doesn't exist
            log_dir = os.path.dirname(LOG_FILE)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # Delete previous file and create a new one
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write("=== SLwebcams Log initialized on {} ===\n".format(timestamp))
                f.write("=== Maximum size: {}KB ===\n\n".format(int(MAX_LOG_SIZE / 1024)))

            return True
        except Exception as e:
            print("Error initializing log: {}".format(e))
            return False

    @staticmethod
    def enhanced_log(message, level="INFO", processo=None):
        """
        Log a message to the log file with detailed context information.

        Args:
            message (str): The message to log
            level (str): Log level (INFO, WARNING, ERROR, DEBUG)
            processo (str): Specific process/function name (optional)
        """
        try:
            # Get call stack information
            stack = inspect.stack()
            # stack[1] is the calling function
            caller_frame = stack[1]
            # Get calling file name (without path)
            caller_file = os.path.basename(caller_frame.filename)
            # Get calling function name
            caller_function = caller_frame.function
            # Get line number
            line_number = caller_frame.lineno

            # Current timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Format log message with process information
            process_info = ":{}".format(processo) if processo else ""
            log_entry = "[{}] [{}] [{}:{}{}:{}] {}\n".format(
                timestamp, level, caller_file, caller_function,
                process_info, line_number, message
            )

            # Check if log file exists, otherwise create it
            if not os.path.exists(LOG_FILE):
                SLLogger.initialize()

            # Check file size
            if os.path.getsize(LOG_FILE) >= MAX_LOG_SIZE:
                # If file exceeds maximum size, delete the first half
                SLLogger._rotate_log()

            # Append message to log file
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_entry)

            return True
        except Exception as e:
            print("Error writing to log: {}".format(e))
            return False

    @staticmethod
    def _rotate_log():
        """
        Handle log file rotation when it exceeds the maximum size.
        Keeps the second half of the file and adds a rotation message.
        """
        try:
            # Read file content
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                content = f.read()

            # Calculate half of the content (approximate)
            half_size = len(content) // 2
            new_content = content[half_size:]

            # Write the second half to the file with a rotation message
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write("=== Log rotated on {} - Previous content truncated ===\n\n".format(timestamp))
                f.write(new_content)

            return True
        except Exception as e:
            print("Error rotating log: {}".format(e))
            return False

    @staticmethod
    def log_exception(e, additional_info=""):
        """
        Log an exception to the log file with full traceback.

        Args:
            e (Exception): The exception to log
            additional_info (str): Additional information about the exception
        """
        try:
            # Get exception traceback
            tb = traceback.format_exc()

            # Format error message
            error_message = "EXCEPTION: {}\n".format(str(e))
            if additional_info:
                error_message += "INFO: {}\n".format(additional_info)
            error_message += "TRACEBACK:\n{}".format(tb)

            # Log the error
            SLLogger.enhanced_log(error_message, "ERROR")

            return True
        except Exception as e:
            print("Error logging exception: {}".format(e))
            return False


def enhanced_log(message, level="INFO", processo=None):
    """
    Utility function to log a message.
    Wrapper for SLLogger.enhanced_log.

    Args:
        message (str): The message to log
        level (str): Log level (INFO, WARNING, ERROR, DEBUG)
        processo (str): Specific process/function name (optional)
    """
    return SLLogger.enhanced_log(message, level, processo)


def log_exception(e, additional_info=""):
    """
    Utility function to log an exception.
    Wrapper for SLLogger.log_exception.

    Args:
        e (Exception): The exception to log
        additional_info (str): Additional information about the exception
    """
    return SLLogger.log_exception(e, additional_info)
