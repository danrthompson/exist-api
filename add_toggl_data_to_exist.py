import os

import json
import pytz
import requests
from datetime import timedelta


import maya
from toggl.TogglPy import Toggl

NYC = pytz.timezone("America/New_York")
TOKEN = os.environ.get("EXIST_CLIENT_PAT")


def get_durations_and_starts():

    toggl = Toggl()

    toggl.setAPIKey(os.environ.get("TOGGL_API_KEY"))

    times_resp = toggl.request(
        "https://api.track.toggl.com/api/v8/time_entries?start_date=2022-09-10T15%3A42%3A46%2B02%3A00"
    )

    work_projs = set()
    non_work_proj = set()

    times = []
    for time in times_resp:
        if "pid" not in time:
            continue
        pid = time["pid"]
        if pid in non_work_proj:
            continue
        if pid not in work_projs:
            project = toggl.getProject(pid)
            cid = project["data"]["cid"]
            if cid != 61372545:
                non_work_proj.add(pid)
                continue
            work_projs.add(pid)
        times.append(time)

    durs = {}
    starts = {}
    for time in times:
        date_added = False
        dt = maya.parse(time["start"]).datetime()
        dt = dt.astimezone(NYC)
        dtime = dt.time()
        dt = dt.date()
        if dtime.hour < 8:
            dt -= timedelta(days=1)
            date_added = True
        dur = durs.get(dt, 0)
        dur += time["duration"]
        durs[dt] = int(dur / 60)
        if dt not in starts:
            if date_added:
                starts[dt] = 22 * 60
            else:
                starts[dt] = dtime.hour * 60 + dtime.minute

    return durs, starts


def acquire_release_attribute(token, attribute, acquire=True):
    if acquire:
        url = "https://exist.io/api/2/attributes/acquire/"
    else:
        url = "https://exist.io/api/2/attributes/release/"

    # make the json string to send to Exist
    body = json.dumps([{"name": attribute}])

    # make the POST request, sending the json as the POST body
    # we need a content-type header so Exist knows it's json
    response = requests.post(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-type": "application/json",
        },
    )

    if response.status_code == 200:
        # a 200 status code indicates a successful outcome
        print("Acquired successfully.")
    else:
        # print the error if something went wrong
        data = response.json()
        print("Error:", data)


def make_update(attribute, date, value):
    return {"name": attribute, "date": date, "value": value}


def update_attributes(token, updates):
    # make the json string to send to Exist
    body = json.dumps(updates)

    # make the POST request, sending the json as the POST body
    # we need a content-type header so Exist knows it's json
    response = requests.post(
        "https://exist.io/api/2/attributes/update/",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-type": "application/json",
        },
    )

    if response.status_code == 200:
        # a 200 status code indicates a successful outcome
        print("Updated successfully.")
    else:
        # print the error if something went wrong
        data = response.json()
        print("Error:", data)


# call the function with the attribute we're after
acquire_release_attribute(TOKEN, "work_time", acquire=True)
acquire_release_attribute(TOKEN, "time_started_work", acquire=True)

durs, starts = get_durations_and_starts()

updates = []
for dt, dur in durs.items():
    dts = f"{dt.year}-{dt.month}-{dt.day}"
    updates.append(make_update("work_time", dts, dur))

update_attributes(TOKEN, updates)


updates = []
for dt, start in starts.items():
    dts = f"{dt.year}-{dt.month}-{dt.day}"
    updates.append(make_update("time_started_work", dts, start))

update_attributes(TOKEN, updates)
