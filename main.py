import argparse
import json
import logging
import sys

from os.path import join, dirname, realpath, exists


from team_scrapper.app.version import TEAM_SCRAPPER_VERSION
from team_scrapper.common import config as scrapper_config
from team_scrapper.common.client import Client

PROJECT_DIRECTORY = dirname(realpath(__file__))
ATTACHMENTS_DIRECTORY = join(PROJECT_DIRECTORY, "attachments")

logging.basicConfig(stream=sys.stdout,
                    format="%(levelname)s %(asctime)s - %(message)s",
                    level=logging.INFO)

logging.info(f"Team Scrapper Version: {TEAM_SCRAPPER_VERSION}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse JIRA JQL requests")
    parser.add_argument('--query',
                        type=str,
                        default="issues",
                        help="Print data to stdout or save to file")
    parser.add_argument('--format',
                        type=str,
                        default="table",
                        help="Specify out format in json, table or sheet (Excel spreadsheet")

    args = parser.parse_args()
    config = scrapper_config.init()
    query = args.query.casefold()
    cache_file = join(config.base_dir, f"{query}.json")

    if not exists(cache_file):
        request = Client.create_cache(config=config, query=query, format=args.format)

        with open(cache_file, 'w') as outfile:
            logging.info(f"Writing data to {cache_file}")
            json.dumps(request, outfile)

    with open(cache_file, 'r') as content:
        logging.info(f"Reading JSON data: {cache_file}")

        data = json.load(content)
        query = args.query.casefold()
        output_format = args.format.casefold()

        if query == "users":
            users = Client.get_users(data)
            Client.print_data(config, users, output_format)
        elif query == "attachments":
            attachments = Client.get_attachments(config, data)
            Client.print_data(config, attachments, output_format)
