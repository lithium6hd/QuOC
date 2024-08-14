"""
Simple logging template
"""
import logging
import sys

APP_LOGGER_NAME = 'FewFermions'

def setup_applevel_logger(logger_level=logging.INFO, logger_name = APP_LOGGER_NAME, file_name=None):
    """
    Initialize logger. Logs are going to be printed to std out. You can specify a file as well.
    :param logger_level:
    :param logger_name:
    :param file_name:
    :return: logger
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logger_level)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(sh)
    if file_name:
        fh = logging.FileHandler(file_name)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger

def get_logger(module_name):
    """
    Get logger (if you want to log something)
    :param module_name:
    :return: logger
    """
    return logging.getLogger(APP_LOGGER_NAME).getChild(module_name)