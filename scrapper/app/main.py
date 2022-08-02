import argparse
import json
import logging
import sys

from os.path import join, dirname, realpath, exists

from scrapper.app.version import SCRAPPER_VERSION
from scrapper.common import config as scrapper_config
from scrapper.common.client import Client

PROJECT_DIRECTORY = dirname(realpath(__file__))
ATTACHMENTS_DIRECTORY = join(PROJECT_DIRECTORY, "attachments")

logging.basicConfig(stream=sys.stdout,
                    format="%(levelname)s %(asctime)s - %(message)s",
                    level=logging.INFO)

logging.info(f"JIRA Scrapper Version: {SCRAPPER_VERSION}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse JIRA JQL requests")
    parser.add_argument('--query',
                        type=str,
                        default="issues",
                        help="Query users, issues or attachments")
    parser.add_argument('--output_format',
                        type=str,
                        default="sheet",
                        help="Specify out format in json, table or sheet (Excel spreadsheet")

    config = scrapper_config.init()
    args = parser.parse_args()
    query = args.query.casefold()
    output_format = args.output_format.casefold()
    cache_file = join(config.base_dir, f"{query}.json")

    if not exists(cache_file):
        print(f"Creating cache for: {cache_file}")
        request = Client(config=config).create_cache(config=config, query=query)

    with open(cache_file, 'r') as content:
        logging.info(f"Reading JSON data: {cache_file}")
        data = json.load(content)

        if query == "users":
            results = Client.get_users(config, data)
        elif query == "issues":
            results = Client.get_issues(config, data)
        elif query == "attachments":
            results = Client.get_attachments(config, data)
        Client.print_data(config=config, query=query, data=results, output_format=output_format)
