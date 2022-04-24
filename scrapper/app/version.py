"""
Retrieve the exact version of the application from the version.json file.
If the file is not available, display a dev version.
"""
import json
import os

import scrapper

PACKAGE_DIRECTORY = scrapper.__path__[0]
MAIN_DIRECTORY = os.path.dirname(PACKAGE_DIRECTORY)
VERSION_FILEPATH = os.path.join(MAIN_DIRECTORY, "version.json")


def get_app_version():
    """
    Retrieve the latest application version of the icebreaker package.
    If a version file is not found, then default to a dev version.
    """
    if not os.path.isfile(VERSION_FILEPATH):
        return "dev"

    with open(VERSION_FILEPATH, "r", encoding="utf-8") as handler:
        content = json.load(handler)
        version_obj = content.get("version", {})
        return version_obj.get("full", "dev")


SCRAPPER_VERSION = get_app_version()
