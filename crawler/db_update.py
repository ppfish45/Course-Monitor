"""
db_update.py:
one-off execution to crawl the latest data and upload them to the db
"""

import db
import os
import time
import crawler
import datetime
import configparser

from tqdm import tqdm

PROJECT_PATH = os.path.join(os.path.dirname(__file__), "..")
CONFIG_PATH = os.path.join(PROJECT_PATH, ".course-monitor")

config = configparser.ConfigParser()
config.read(CONFIG_PATH)


def get_index_and_sem_name(year, sem):
    sem_suf = {
        "Fall": 10,
        "Winter": 20,
        "Spring": 30,
        "Summer": 40,
    }

    if sem == "Spring" or sem == "Summer":
        year -= 1

    yr_n = year % 100

    index = yr_n * 100 + sem_suf[sem]
    name = "{}-{} {}".format(year, yr_n + 1, sem)

    return (index, name)


def get_current_semester(now):
    """
    Fall: Aug 20 - Sep 20
    Winter: Nov 10 - Jan 20
    Spring: Jan 15 - Feb 25
    Summer: Apr 20 - Jul 20
    """

    """
    Naming convention:
    {
        'name': '2021-22 Summer',
        'semCode': 2140,
    },
    {
        'name': '2021-22 Spring',
        'semCode': 2130,
    },
    {
        'name': '2021-22 Winter',
        'semCode': 2120,
    },
    {
        'name': '2021-22 Fall',
        'semCode': 2110,
    },
    """

    sem_range = [
        {
            "name": "Fall",
            "start": datetime.date(2, 8, 20),
            "end": datetime.date(2, 9, 20),
        },
        {
            "name": "Winter",
            "start": datetime.date(2, 11, 10),
            "end": datetime.date(3, 1, 20),
        },
        {
            "name": "Winter",
            "start": datetime.date(1, 11, 10),
            "end": datetime.date(2, 1, 20),
        },
        {
            "name": "Spring",
            "start": datetime.date(2, 1, 15),
            "end": datetime.date(2, 2, 25),
        },
        {
            "name": "Summer",
            "start": datetime.date(2, 4, 20),
            "end": datetime.date(2, 7, 20),
        },
    ]

    yr = now.year - 2
    now = now.replace(year=2)

    possible_index = []

    for sem in sem_range:
        if now >= sem["start"] and now <= sem["end"]:
            real_yr = yr + sem["start"].year
            possible_index.append(get_index_and_sem_name(real_yr, sem["name"]))

    return possible_index


assert(get_current_semester(datetime.date(2023, 1, 10)) == [
    (2220, "2022-23 Winter"),
    (2230, "2022-23 Spring")
])
assert(get_current_semester(datetime.date(2023, 1, 22)) == [
    (2230, "2022-23 Spring")
])
assert(get_current_semester(datetime.date(2023, 4, 15)) == [])
assert(get_current_semester(datetime.date(2023, 4, 30)) == [
    (2240, "2022-23 Summer")
])
assert(get_current_semester(datetime.date(2023, 6, 30)) == [
    (2240, "2022-23 Summer")
])
assert(get_current_semester(datetime.date(2023, 7, 30)) == [])
assert(get_current_semester(datetime.date(2023, 8, 30)) == [
    (2310, "2023-24 Fall")
])
assert(get_current_semester(datetime.date(2023, 9, 30)) == [])
assert(get_current_semester(datetime.date(2023, 12, 1)) == [
    (2320, "2023-24 Winter")
])


def process(index, name, client: db.DBClient, timestamp):
    res, _ = crawler.crawl(index, generate_md5=False)

    print("process semester [{}] [{}]".format(index, name))
    print("timestamp = ", timestamp)

    # update default
    print("\tupdating default collection ...")
    defColl = client.GetCollection(config["mongodb"]["defaultCollName"])
    defColl.update_one({
        "semCode": index,
    }, {
        "$set": {
            "semCode": index,
            "name": name
        }
    }, upsert=True)

    # update semester
    print("\tupdating semester collection ...")
    semColl = client.GetCollection(config["mongodb"]["semesterCollName"])
    course_list = [*res]
    if semColl.count_documents({"semCode": index}) == 0:
        semColl.insert_one({
            "semCode": index,
            "startTime": timestamp,
            "endTime": timestamp,
            "courses": course_list
        })
    else:
        semColl.update_one({
            "semCode": index
        }, {
            "$set": {
                "endTime": timestamp,
                "courses": course_list,
            }
        })

    # update course
    print("\tupdating course collection ...")
    corColl = client.GetCollection(config["mongodb"]["courseCollName"])
    for course in tqdm(course_list, leave=False):
        elt = res[course]
        sections = [e["section"] for e in elt["course_slots"]]
        corColl.update_one({
            "semCode": index,
            "name": course
        }, {
            "$set": {
                "semCode": index,
                "name": course,
                "sections": sections
            }
        }, upsert=True)

    # update sections
    print("\tupdating section collection ...")
    secColl = client.GetCollection(config["mongodb"]["sectionCollName"])
    for course in tqdm(course_list, leave=False):
        elt = res[course]["course_slots"]
        for e in elt:
            sec = e["section"]

            filter = {
                "semCode": index,
                "name": course,
                "section": sec
            }
            data = {
                "quota": int(e["quota"]),
                "enroll": int(e["enrol"]),
                "avail": int(e["avail"]),
                "wait": int(e["wait"])
            }

            doc = secColl.find_one(filter)
            if doc is None:
                secColl.insert_one({
                    **filter,
                    "data": [
                        {
                            "timestamp": timestamp,
                            **data
                        }
                    ]
                })
            else:
                # check the last data point
                last = doc["data"][-1]
                same = True

                if last["avail"] != data["avail"] or \
                    last["enroll"] != data["enroll"] or \
                    last["quota"] != data["quota"] or \
                        last["wait"] != data["wait"]:
                    same = False

                if not same:
                    secColl.update_one(filter, {
                        "$set": {
                            **filter,
                            "data": [
                                *doc["data"],
                                {
                                    "timestamp": timestamp,
                                    **data
                                }
                            ]
                        }
                    })


if __name__ == "__main__":
    now = datetime.date.today()
    client = db.DBClient()
    sems = get_current_semester(now)

    if len(sems) == 0:
        print("no semester available")

    for index, name in sems:
        timestamp = int(time.time() * 1000)
        process(index, name, client, timestamp)
