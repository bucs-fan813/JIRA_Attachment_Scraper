import json
import logging
import urllib3
import os
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
        output = []
        url = f"{config.config[query.upper()]}"

        json_file = join(config.base_dir, f"{query}.json")
        username = config.username if config.username else getpass(prompt='Enter your username: ')
        password = config.password if config.password else getpass(prompt='Enter your password: ')

        with requests.get(url, auth=HTTPBasicAuth(username, password)) as content:

            if "issues" in content.json():
                while len(content.json()['issues']) > 0:
                    logging.info(f"Getting {query}: {start_index} - {start_index + 1000}")
                    output += content.json()['issues']
                    start_index += 1000
                    next_url = "&".join([url, f"startAt={start_index}"])

                    logging.info(f"Fetching {next_url}")
                    content = requests.get(next_url, auth=HTTPBasicAuth(username, password))
                logging.info(f"Writing data to {json_file}")
                with open(json_file, 'a') as outfile:
                    json.dump(output, outfile)
            else:
                while len(content.json()):
                    logging.info(f"Getting {query}: {start_index} - {start_index + 1000}")
                    output += content.json()
                    start_index += 1000
                    next_url = "&".join([url, f"startAt={start_index}"])

                    logging.info(f"Fetching {next_url}")
                    content = requests.get(next_url, auth=HTTPBasicAuth(username, password))
                logging.info(f"Writing data to {json_file}")
                with open(json_file, 'a') as outfile:
                    json.dump(output, outfile)

    def get_users(self, data: dict) -> list:
        users = []
        if data:
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

    def get_issues(self, data: dict) -> list:
        issues = []
        if not data:
            return issues
        bar = Bar('Loading issues', max=len(data), suffix='%(percent)d%% [%(index)s / %(max)s]')
        for issue in data:
            bar.next()
            issues.append(issue)
        bar.finish()
        logging.info(f"Loaded {len(issues)} issues")
        return issues

    def get_attachments(config: ApiConfig, data: dict) -> list:
        attachments = []
        if not data:
            return attachments
        bar = Bar('Loading Attachments', max=len(data), suffix='%(percent)d%% [%(index)s / %(max)s]')
        username = config.username if config.username else getpass(prompt='Enter your username: ')
        password = config.password if config.password else getpass(prompt='Enter your password: ')
        for issue in data:
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
                            logging.info(f"Downloading {r.url} to -> {attachment_file} [{r.status_code}]")
                            open(attachment_file, 'wb+').write(r.content)
                    except urllib3.exceptions.HTTPError as e:
                        print(e)
                    attachments.append(item)
        bar.finish()
        logging.info(f"Loaded {len(attachments)} attachments")
        return attachments

    def print_data(config: ApiConfig, query: str, data: list, output_format: Optional[str] = "table"):
        if query == "attachments":
            return
        timestamp = f"{datetime.now():%Y%m%dT%H%M%S}"
        if output_format == "table":
            print(pd.DataFrame(data))
        elif output_format == "json":
            filename = join(config.output_directory, f"{query}@{timestamp}.json")
            with open(filename, 'w') as outfile:
                logging.info(f"Writing data to {filename}")
                json.dump(data, outfile)
        elif output_format == "sheet":
            filename = join(config.output_directory, f"{query}@{timestamp}.xlsx")
            if not os.path.exists(config.output_directory):
                os.makedirs(config.output_directory)
            writer = pd.ExcelWriter(filename, engine="xlsxwriter",
                                    engine_kwargs={'options': {'strings_to_numbers': True}})
            pd.DataFrame(data).to_excel(writer, sheet_name=timestamp)
            logging.info(f"Created: {filename}")
            writer.save()
