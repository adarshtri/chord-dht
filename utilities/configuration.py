import json
import os
from constants.configuration_constants import ConfigurationConstants


__all__ = ["ConfigurationManager"]


class Configuration(object):

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
