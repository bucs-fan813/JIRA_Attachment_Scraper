"""Provides service configuration values based on the .env file"""
import logging
from os import path
from os.path import join, exists

from dotenv import dotenv_values

import scrapper

LOGGER = logging.getLogger(__name__)
BASE_DIR = path.dirname(scrapper.__path__._path[0])  # pylint: disable=protected-access


class ApiConfig:
    """General configurations that are needed for the service (REST API)."""

    def __init__(self, config):
        self.config = config
        self.username = config["USERNAME"]
        self.password = config["PASSWORD"]
        self.host = config["HOST"]
        self.base_dir = BASE_DIR
        self.env_file = join(BASE_DIR, ".env")
        self.output_directory = join(self.base_dir, "output")
        self.max_results = 1000

    @property
    def get_max_results(self):
        """The default number of results for JQL queries"""
        return self.max_results


API: ApiConfig = None


def init(config_path=None):
    """Initialize the global configuration variables by parsing the .env"""

    # pylint: disable=global-statement
    global API

    if not config_path:
        env_file = join(BASE_DIR, ".env")
        assert exists(env_file), ".env variables are not set"
        config = dotenv_values(env_file)

    assert "HOST" in config, \
        f'Missing the required .env settings in configurations in file {config_path}'
    API = ApiConfig(config)

    logging.debug(f'Configurations were loaded:\n\tScrapper: {API.__dict__}')
    return API if API else None
