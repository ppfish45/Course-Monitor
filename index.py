import fcntl
import tqdm
import json
import glob
import sys
import os
import re

CODE = sys.argv[1]
PATH = sys.argv[2]
INDEX_DIR = os.path.join(PATH, 'index', CODE)
COURSE_DIR = os.path.join(INDEX_DIR, 'courses')
HIST_DIR = os.path.join(PATH, 'hist', CODE)

os.makedirs(COURSE_DIR, exist_ok = True)

if __name__ == '__main__':

    ret = dict()

    file_list = glob.glob(os.path.join(HIST_DIR, '*.json'))
    file_list.sort()

    start_time = 0
    end_time = 0

    with tqdm.tqdm(total = len(file_list)) as bar:
        for file_name in file_list:
            timestamp = int(int(os.path.split(file_name)[1].split('.')[0]) / 1000)
            if start_time == 0:
                start_time = timestamp            
            end_time = timestamp
            with open(file_name, 'r') as file:
                fcntl.flock(file.fileno(), fcntl.LOCK_SH)
                data = json.load(file)
            for course in data:
                course_data = data[course]
                if course not in ret:
                    ret[course] = dict()
                sections = course_data['course_slots']
                for section in sections:
                    sec_name = section['section']
                    if sec_name not in ret[course]:
                        ret[course][sec_name] = []
                    delta = {
                        'timestamp' : timestamp,
                        'avail' : int(section['avail']),
                        'enroll' : int(section['enrol']),
                        'quota' : int(re.match('\d+', section['quota'])[0]),
                        'wait' : int(section['wait'])
                    }
                    ret[course][sec_name].append(delta)
            bar.update(1)
    
    with tqdm.tqdm(total = len(ret)) as bar:
        for course in ret:
            file_path = os.path.join(COURSE_DIR, course + '.json')
            with open(file_path, 'w') as file:
                fcntl.flock(file.fileno(), fcntl.LOCK_EX)
                json.dump(ret[course], file)
            bar.update(1)

    sem_info = {
        'semCode' : int(CODE),
        'startTime' : start_time,
        'endTime' : end_time,
        'courses' : list(ret.keys())
    }
    file_path = os.path.join(INDEX_DIR, 'info.json')
    with open(file_path, 'w') as file:
        fcntl.flock(file.fileno(), fcntl.LOCK_EX)
        json.dump(sem_info, file)
