import logging
import logging.handlers
from logging.handlers import RotatingFileHandler
import os
import sys
from logging import FileHandler

loggers = []
logger = logging.getLogger()
log_file_name = 'QnAKB.log'
log_location = None
file_format_string = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
console_format_string = "[%(asctime)s] [%(levelname)s]: %(message)s"

if log_location is None:
    log_location = "."


def setup_root_logger():
    log_location_path = os.path.join(log_location, log_file_name)
    print("Application log location: " + log_location_path)

    logger = logging.getLogger()
    logging.basicConfig(format=console_format_string, filemode='a+', level=logging.INFO,
                        datefmt="%I:%M:%S %p")
    handler = RotatingFileHandler(log_location_path, maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(logging.Formatter(file_format_string))
    logger.addHandler(handler)
    logging.info('Working directory path : %s', os.getcwd())


setup_root_logger()


def set_up_logging(logger_name=None, use_seperate_file=False):
    if logger_name is None:
        logger = logging.getLogger()
        return logger
    else:
        logger = logging.getLogger(logger_name)
        if use_seperate_file and not logger.handlers:
            handler = FileHandler(os.path.join(log_location, str(logger_name) + ".log"), mode='a')
            handler.setFormatter(logging.Formatter(file_format_string))
            logger.addHandler(handler)
        return logger


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Application failed with an unknown error.", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception