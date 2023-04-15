import db
import os
import json
import glob
import configparser
from tqdm import tqdm

sem_list = [
    {
        'name': '2022-23 Spring',
        'semCode': 2230,
    },
    {
        'name': '2022-23 Fall',
        'semCode': 2210,
    },
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
    {
        'name': '2020-21 Spring',
        'semCode': 2030,
    },
    {
        'name': '2020-21 Winter',
        'semCode': 2020
    },
    {
        'name': '2020-21 Fall',
        'semCode': 2010
    },
    {
        'name': '2019-20 Summer',
        'semCode': 1940
    },
    {
        'name': '2019-20 Spring',
        'semCode': 1930
    },
    {
        'name': '2019-20 Winter',
        'semCode': 1920
    },
    {
        'name': '2019-20 Fall',
        'semCode': 1910
    },
    {
        'name': '2018-19 Summer',
        'semCode': 1840
    },
    {
        'name': '2018-19 Spring',
        'semCode': 1830
    }
]

"""
Put the conf and index folder under:
../conf
../index
"""

"""
Collection #1: Default
{
    "name": "2022-23 Spring",
    "semCode": 2230
}
...

Collection #2: Semester
{
    "semCode": 1830, 
    "startTime": 1548302079019, 
    "endTime": 1550289841133, 
    "courses": [
        "COMP1021",
        ...
    ]
}
...

Collection #3: Course
{
    "semCode": 1830,
    "name": "COMP1021",
    "sections": [
        "L1",
        "L2",
        ...
    ]
}

Collection #4: Section
{
    "semCode": 1830,
    "name": "COMP1021",
    "section": "L1",
    "data": [
        {
            "timestamp": 1548302079019,
            "avail": 25,
            "enroll": 0,
            "quota": 25,
            "wait": 0
        },
        ...
    ]
}
"""

PROJECT_PATH = os.path.join(os.path.dirname(__file__), "..")
CONFIG_PATH = os.path.join(PROJECT_PATH, ".course-monitor")

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

def filter_data(data):
    desired_field = ["timestamp", "avail", "enroll", "quota", "wait"]
    res = []
    for item in data:
        res.append({k: v for k, v in item.items() if k in desired_field})
    return res


def upload_default_coll(client: db.DBClient):
    print("upload collection [{}] ..."
          .format(config["mongodb"]["defaultCollName"]))
    coll = client.GetCollection(config["mongodb"]["defaultCollName"])
    for item in tqdm(sem_list, leave=False):
        if coll.count_documents(item) == 0:
            coll.insert_one(item)


def upload_semester_coll(client: db.DBClient):
    print("upload collection [{}] ..."
          .format(config["mongodb"]["semesterCollName"]))
    coll = client.GetCollection(config["mongodb"]["semesterCollName"])
    for sem in tqdm(sem_list, leave=False):
        file_path = os.path.join(
            PROJECT_PATH, "index", str(sem["semCode"]), "info.json")
        with open(file_path, "r") as f:
            elt = json.load(f)
            coll.update_one({
                "semCode": elt["semCode"]
            }, {
                "$set": elt
            }, upsert=True)


def upload_course_and_section_coll(client: db.DBClient):
    print("upload collection [{}] ..."
          .format(config["mongodb"]["courseCollName"]))
    course_coll = client.GetCollection(config["mongodb"]["courseCollName"])
    section_coll = client.GetCollection(config["mongodb"]["sectionCollName"])
    for sem in tqdm(sem_list, leave=False):
        semCode = sem["semCode"]
        course_path = os.path.join(
            PROJECT_PATH, "index", str(semCode), "courses"
        )
        course_file_list = glob.glob(os.path.join(course_path, "*.json"))
        for path in tqdm(course_file_list, leave=False):
            course = os.path.split(path)[1].split(".")[0]
            with open(path, "r") as f:
                obj = json.load(f)
                section_list = [*obj]

                # upload section list
                course_coll.update_one({
                    "semCode": semCode,
                    "name": course
                }, {
                    "$set": {
                        "semCode": semCode,
                        "name": course,
                        "sections": section_list,
                    }
                }, upsert=True)

                # upload data for each section
                for sec, data in obj.items():
                    section_coll.update_one({
                        "semCode": semCode,
                        "name": course,
                        "section": sec,
                    }, {
                        "$set": {
                            "semCode": semCode,
                            "name": course,
                            "section": sec,
                            "data": filter_data(data),
                        }
                    }, upsert=True)


if __name__ == '__main__':
    client = db.DBClient()
    upload_default_coll(client)
    upload_semester_coll(client)
    upload_course_and_section_coll(client)
