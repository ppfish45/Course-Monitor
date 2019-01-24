import os
import json
import glob
import time

USER_INFO = os.path.join('.', 'receiver')
TIMESTAMP = time.time()
LATEST_LOG = os.path.join('.', 'conf', INDEX + '_latest.json')

with open(LATEST_LOG, 'r') as file:
    latest_log = json.load(file)

def send(index):
    for filename in glob.glob(os.path.join(USER_INFO, '*.json')):
        ur = os.path.split(filename)[1].split('.')[0]
        with open(filename, 'r') as file:
            infos = json.load(file)
        last_time = infos['last']
        interval = infos['interval']
        cur_ver = infos['cur_version']
        watch_list = infos['watch_list']
        old_course = []
        new_course = []
        if TIMESTAMP - last_time > interval * 1000:
            for course in watch_list:
                if latest_log[course]['timestamp'] > cur_ver:
                    old_course.append(get_version(course, cur_ver))
                    new_course.append(get_version(course, latest_log[course]['timestamp']))