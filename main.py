import json
import requests

from os.path import join, dirname, realpath, exists
from requests.auth import HTTPBasicAuth
from dotenv import dotenv_values
from getpass import getpass

PROJECT_DIRECTORY = dirname(realpath(__file__))
JSON_FILE = join(PROJECT_DIRECTORY, "response.json")
ENV_FILE = join(PROJECT_DIRECTORY, ".env")

if __name__ == "__main__":
    if not exists(JSON_FILE):
        config = dotenv_values(ENV_FILE)
        URL = config["URL"] if len(config) > 0 else None
        if URL:
            raise ValueError
        username = config["USERNAME"] if config["USERNAME"] else getpass(prompt='Enter your username: ')
        password = config["PASSWORD"] if config["PASSWORD"] else getpass(prompt='Enter your password? ')

        with requests.get(URL, auth=HTTPBasicAuth(username, password)) as content:
            print(content)
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
                    print(f"{item['key']} -> {item['url']}")
                    attachments += [item]
        print(f"Found: {len(attachments)} attachments")
