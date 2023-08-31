import os

from multiprocessing import AuthenticationError
import requests
import datetime

# CLIENT_PERSONAL_TOKEN = os.environ.get('EXIST_CLIENT_PAT')
TOKEN = os.environ.get("EXIST_PERSONAL_TOKEN")

URL = "https://exist.io/api/2/attributes/with-values/"


def call_api(params=None):
    response = requests.get(
        URL,
        params=params,
        headers={"Authorization": f"Token {TOKEN}"},
    )

    if response.status_code != 200:
        raise AuthenticationError(f"Auth error. {response.content}")

    return response.json()


def get_attribute_from_api(attr_name):
    return call_api({"attributes": attr_name})


def get_all_attributes_from_api():
    return call_api()


def get_all_attributes():
    data = get_all_attributes_from_api()

    attributes = {}
    for attribute in data["results"]:
        # grab the fields we want from the json
        label = attribute["label"]
        value = attribute["values"][0]["value"]
        # and store them as key/value
        attributes[label] = value

    for label, value in attributes.items():
        print(f"{label}: {value}")


print(get_all_attributes_from_api())
print(get_attribute_from_api("C"))
print(get_all_attributes())
