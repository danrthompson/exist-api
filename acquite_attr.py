import os

import requests
import json

URL = "https://exist.io/api/2/attributes/acquire/"
TOKEN = os.environ.get("EXIST_CLIENT_PAT")


def acquire_attribute(attribute):
    # make the json string to send to Exist
    body = json.dumps([{"template": attribute}])

    # make the POST request, sending the json as the POST body
    # we need a content-type header so Exist knows it's json
    response = requests.post(
        URL,
        data=body,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-type": "application/json",
        },
    )

    if response.status_code == 200:
        # a 200 status code indicates a successful outcome
        print("Acquired successfully.")
    else:
        # print the error if something went wrong
        data = response.json()
        raise RuntimeError(f"Error: {data}")


# call the function with the attribute we're after
acquire_attribute("C")
