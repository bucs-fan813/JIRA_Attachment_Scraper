import json
import requests
import urllib3.exceptions

from getpass import getpass
from http import HTTPStatus
from os import makedirs
from os.path import join, dirname, realpath, exists
from dotenv import dotenv_values
from requests.auth import HTTPBasicAuth

PROJECT_DIRECTORY = dirname(realpath(__file__))
ATTACHMENTS_DIRECTORY = join(PROJECT_DIRECTORY, "attachments")
JSON_FILE = join(PROJECT_DIRECTORY, "response.json")
ENV_FILE = join(PROJECT_DIRECTORY, ".env")
USERNAME = ''
PASSWORD = ''

if __name__ == "__main__":
    config = dotenv_values(ENV_FILE)
    USERNAME = config["USERNAME"] if config["USERNAME"] else getpass(prompt='Enter your username: ')
    PASSWORD = config["PASSWORD"] if config["PASSWORD"] else getpass(prompt='Enter your password? ')

    if not exists(JSON_FILE):
        URL = config["URL"] if len(config) > 0 else None

        with requests.get(URL, auth=HTTPBasicAuth(USERNAME, PASSWORD)) as content:
            with open(JSON_FILE, 'w') as outfile:
                print(f"Writing data to {JSON_FILE}")
                json.dump(content.json(), outfile)

    attachments = []
    with open(JSON_FILE, 'r') as content:
        print("Reading JSON data")
        data = json.load(content)

        for issue in data["issues"]:
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
                    ISSUE_DIRECTORY = join(ATTACHMENTS_DIRECTORY, item["key"])
                    ATTACHMENT_FILE = join(ISSUE_DIRECTORY, attachment["filename"])

                    if not exists(ISSUE_DIRECTORY):
                        makedirs(ISSUE_DIRECTORY)

                    try:
                        r = requests.get(item['url'], auth=HTTPBasicAuth(USERNAME, PASSWORD), allow_redirects=True)
                        if r.status_code == HTTPStatus.OK:
                            print(f"Downloading {r.url} to -> {ATTACHMENT_FILE} [{r.status_code}]")
                            open(ATTACHMENT_FILE, 'wb+').write(r.content)
                    except urllib3.exceptions.HTTPError as e:
                        print(e)
                    attachments += [item]
        print(f"Found: {len(attachments)} attachments")
