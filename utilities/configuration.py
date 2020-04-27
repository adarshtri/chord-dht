"""
Author: Adarsh Trivedi
Module to handle configuration files and provides a configuration object for cleaner
accessibility for configuration properties throughout the project.
"""


import json
import os
from constants.configuration_constants import ConfigurationConstants


__all__ = ["ConfigurationManager"]


class Configuration(object):

    """
    Author: Adarsh Trivedi
    Object representation class of configuration files. Could be considered as serialization class
    for the configuration file. Invalid or missing properties in configuration files are not
    handled. Assumes configuration file provided is correct.
    """

    def __init__(self, config_file):

        self._config_file = config_file
        self._config = None
        self._set_config()

    def get_advertised_ip(self):
        return self._config[ConfigurationConstants.CHORD_ADVERTISED_IP]

    def get_socket_port(self):
        return self._config[ConfigurationConstants.CHORD_SOCKET_PORT]

    def get_chord_server_ip(self):
        return self._config[ConfigurationConstants.CHORD_SERVER_IP]

    def get_m_bits(self):
        return self._config[ConfigurationConstants.CHORD_M_BITS]

    def get_stabilize_interval(self):
        return self._config[ConfigurationConstants.CHORD_STABILIZE_INTERVAL]

    def get_log_file(self):
        return self._config[ConfigurationConstants.LOG_FILE]

    def get_should_log_to_console(self):
        return int(self._config[ConfigurationConstants.LOG_TO_CONSOLE])

    def get_log_frequency_interval(self):
        return int(self._config[ConfigurationConstants.LOG_FREQUENCY_INTERVAL])

    def get_log_frequency_interval_unit(self):
        return self._config[ConfigurationConstants.LOG_FREQUENCY_UNIT]

    def get_log_frequency_backup_count(self):
        return self._config[ConfigurationConstants.LOG_FREQUENCY_BACKUP_COUNT]

    def _set_config(self):

        try:
            with open(self._config_file, 'r') as f:
                self._config = f.read()

            try:
                self._config = json.loads(self._config)
            except json.JSONDecodeError:
                print("Configuration file provided not in JSON format.")
                exit(1)

        except FileNotFoundError:
            print("Configuration file provided not found.")
            exit(1)


class ConfigurationManager:

    """
    Author: Adarsh Trivedi
    This class makes sure only single instance of the Configuration class is present.
    There is no need to create multiple instance of Configuration class hence
    this manager is required.
    """

    configuration = None

    @staticmethod
    def get_configuration():

        if not ConfigurationManager.configuration:
            ConfigurationManager.configuration = \
                Configuration(os.environ[ConfigurationConstants.CHORD_CONFIGURATION_FILE_ENV_VARIABLE])

        return ConfigurationManager.configuration

    @staticmethod
    def reset_configuration():
        ConfigurationManager.configuration = None
        ConfigurationManager.get_configuration()
