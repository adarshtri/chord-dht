"""
Logging module for the project.
Author: Adarsh Trivedi
"""


import logging
from logging.handlers import TimedRotatingFileHandler
from logging import StreamHandler
from utilities.configuration import ConfigurationManager
import sys


class Logging(object):

    """
    Author: Adarsh Trivedi
    This class creates a timed rotating file logger. The rotation policies are picked
    from the provided configuration file.
    """

    handler = TimedRotatingFileHandler(
        filename=ConfigurationManager.get_configuration().get_log_file(),
        when=ConfigurationManager.get_configuration().get_log_frequency_interval_unit(),
        interval=ConfigurationManager.get_configuration().get_log_frequency_interval(),
        backupCount=ConfigurationManager.get_configuration().get_log_frequency_backup_count())

    console_handler = StreamHandler(stream=sys.stdout)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    @staticmethod
    def get_logger(name):

        logger = logging.getLogger(name)
        logger.addHandler(Logging.handler)
        if ConfigurationManager.get_configuration().get_should_log_to_console():
            print(ConfigurationManager.get_configuration().get_should_log_to_console())
            logger.addHandler(Logging.console_handler)
        logger.setLevel(logging.INFO)
        Logging.handler.setFormatter(Logging.formatter)
        return logger
