import os

from multiprocessing import AuthenticationError
import requests

username = os.getenv("EXIST_USERNAME")
password = os.getenv("EXIST_PASSWORD")

url = "https://exist.io/api/1/auth/simple-token/"

response = requests.post(url, data={"username": username, "password": password})

# make sure the response was 200 OK, meaning no errors
if response.status_code == 200:
    # parse the json object from the response body so we can print the token
    data = response.json()
else:
    raise AuthenticationError(
        "Error with auth. Status code: {}. Resp: {}".format(response.status_code),
        response.text,
    )

token = data["token"]

print(token)
