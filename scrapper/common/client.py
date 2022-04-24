import json
import logging
import urllib3
import requests
import pandas as pd

from getpass import getpass
from os import makedirs
from typing import Optional
from datetime import datetime
from requests.auth import HTTPBasicAuth
from progress.bar import Bar
from os.path import join, exists
from http import HTTPStatus

from scrapper.common.config import ApiConfig


class Client:
    def __init__(self, config):
        self.config = config

    def create_cache(self, config: ApiConfig, query: str = "issues") -> list:
        start_index = 0
        url = f"{config.config[query.upper()]}"
        json_file = join(config.base_dir, f"{query}.json")
        output = []
        username = config.username if config.username else getpass(prompt='Enter your username: ')
        password = config.password if config.password else getpass(prompt='Enter your password: ')
        logging.info(f"Fetching: {url}")

        with requests.get(url, auth=HTTPBasicAuth(username, password)) as content:
            while len(content.json()):
                logging.info(f"Getting users: {start_index} - {start_index + 1000}")
                output += content.json()
                start_index += 1000
                next_url = "&".join([url, f"startAt={start_index}"])
                content = requests.get(next_url, auth=HTTPBasicAuth(username, password))

        with open(json_file, 'w') as outfile:
            logging.info(f"Writing data to {json_file}")
            json.dumps(output, outfile)
        return output if output else None

    def get_users(data: dict) -> list:
        users = []
        bar = Bar('Loading Users', max=len(data), suffix='%(percent)d%% [%(index)s / %(max)s]')

        for user in data:
            bar.next()
            users.append({
                "key": user["key"],
                "name": user["name"],
                "email": user["emailAddress"],
                "displayName": user["displayName"],
                "active": user["active"],
                "deleted": user["deleted"],
                "tz": user["timeZone"],
                "locale": user["locale"]
            })
        bar.finish()
        logging.info(f"Loaded {len(users)} users")
        return users

    def get_attachments(config: ApiConfig, data: dict) -> list:
        attachments = []
        bar = Bar('Loading Attachments', max=len(data["issues"]), suffix='%(percent)d%% [%(index)s / %(max)s]')
        username = config.username if config.username else getpass(prompt='Enter your username: ')
        password = config.password if config.password else getpass(prompt='Enter your password: ')

        for issue in data["issues"]:
            bar.next()
            if issue["fields"]["attachment"]:
                for attachment in issue["fields"]["attachment"]:
                    item = {
                        "file_id": issue["id"],
                        "file_name": attachment["filename"],
                        "mime_type": attachment["mimeType"],
                        "url": attachment["content"],
                        "created": attachment["created"],
                        "key": issue["key"]
                    }
                    if "author" in attachment.keys():
                        item["created_by"] = {
                            "name": attachment["author"]["name"],
                            "email": attachment["author"]["emailAddress"],
                            "display": attachment["author"]["displayName"]
                        }

                    issue_directory = join(config.output_directory, item["key"])
                    attachment_file = join(issue_directory, attachment["filename"])

                    if not exists(issue_directory):
                        makedirs(issue_directory)

                    try:
                        r = requests.get(item['url'], auth=HTTPBasicAuth(username, password), allow_redirects=True)
                        if r.status_code == HTTPStatus.OK:
                            # print(f"Downloading {r.url} to -> {ATTACHMENT_FILE} [{r.status_code}]")
                            open(attachment_file, 'wb+').write(r.content)
                    except urllib3.exceptions.HTTPError as e:
                        print(e)
                    attachments.append(item)
        bar.finish()
        logging.info(f"Loaded {len(attachments)} attachments")
        return attachments

    def print_data(config: ApiConfig, data: list, output_format: Optional[str] = "table"):
        if output_format == "table":
            print(pd.DataFrame(data))
        elif output_format == "json":
            print(json.dumps(data))
        elif output_format == "sheet":
            timestamp = f"{datetime.now():%Y%m%dT%H%M%S}"
            filename = join(config.output_directory, f"{timestamp}.xlsx")
            writer = pd.ExcelWriter(filename, engine="xlsxwriter",
                                    engine_kwargs={'options': {'strings_to_numbers': True}})
            pd.DataFrame(data).to_excel(writer, sheet_name=timestamp)
            logging.info(f"Created: {filename}")
            writer.save()
