import json
import requests
import pandas as pd

from datetime import datetime
from getpass import getpass
from os.path import join, dirname, realpath, exists
from dotenv import dotenv_values
from requests.auth import HTTPBasicAuth
from progress.bar import Bar


PROJECT_DIRECTORY = dirname(realpath(__file__))
JSON_FILE = join(PROJECT_DIRECTORY, "users.json")
ENV_FILE = join(PROJECT_DIRECTORY, ".env")
# pd.set_option('display.max_rows', None)

USERNAME = ''
PASSWORD = ''

if __name__ == "__main__":
    config = dotenv_values(ENV_FILE)
    USERNAME = config["USERNAME"] if config["USERNAME"] else getpass(prompt='Enter your username: ')
    PASSWORD = config["PASSWORD"] if config["PASSWORD"] else getpass(prompt='Enter your password? ')

    if not exists(JSON_FILE):
        URL = config["USERS"] if len(config) > 0 else None
        start_index = 0
        start_url = "&".join([URL, f"startAt={start_index}"])
        output = []
        with requests.get(start_url, auth=HTTPBasicAuth(USERNAME, PASSWORD)) as content:
            while len(content.json()):

                print(f"Getting users: {start_index} {start_index+1000}")
                output += content.json()
                start_index += 1000
                start_url = "&".join([URL, f"startAt={start_index}"])
                content = requests.get(start_url, auth=HTTPBasicAuth(USERNAME, PASSWORD))

        with open(JSON_FILE, 'w') as outfile:
            print(f"Writing data to {JSON_FILE}")
            json.dump(output, outfile)
    users = []
    with open(JSON_FILE, 'r') as content:
        print("Reading JSON data")
        data = json.load(content)
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
    print(pd.DataFrame(users))
    timestamp = f"{datetime.now():%Y%m%dT%H%M%S}"
    filename = join(PROJECT_DIRECTORY, f"{timestamp}.xlsx")
    writer = pd.ExcelWriter(filename, engine="xlsxwriter", engine_kwargs={'options': {'strings_to_numbers': True}})
    pd.DataFrame(users).to_excel(writer, sheet_name=timestamp)
    writer.save()
    print(f"Created: {filename}")
    print(f"Found: {len(users)} users")
