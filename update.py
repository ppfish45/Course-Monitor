import os
import sys
import time
import json
import tqdm
import shutil
import crawler

TIMESTAMP = int(time.time() * 1000)
INDEX = sys.argv[1]
LATEST_LOG = os.path.join('.', 'conf', INDEX + '_latest.json')
LATEST_FILE = os.path.join('.', 'latest', INDEX + '.json')
EXPORT_FILE = os.path.join('.', 'hist', INDEX, str(TIMESTAMP) + '.json')

os.makedirs(os.path.split(EXPORT_FILE)[0], exist_ok = True)
os.makedirs(os.path.split(LATEST_FILE)[0], exist_ok = True)
os.makedirs(os.path.split(LATEST_LOG)[0], exist_ok = True)

def write_update(course_data, md5_data):
    latest_log = None
    new_course_file = dict()
    try:
        with open(LATEST_LOG, 'r') as file:
            latest_log = json.load(file)
        ok = True
    except:
        latest_log = dict()
        ok = False
    with tqdm.tqdm(total = len(md5_data.keys())) as bar:
        for name in md5_data.keys():
            cur_md5 = md5_data[name]
            try:
                latest_md5 = latest_log[name]['md5']
            except:
                latest_md5 = None
                ok = False    
            if not ok or cur_md5 != latest_md5:
                latest_log[name] = dict()
                latest_log[name]['md5'] = cur_md5
                latest_log[name]['timestamp'] = TIMESTAMP
                new_course_file[name] = course_data[name]
            bar.update(1)
    with open(EXPORT_FILE, 'w') as file:
        json.dump(new_course_file, file, sort_keys = True)
    with open(LATEST_LOG, 'w') as file:
        json.dump(latest_log, file, sort_keys = True)

def create_latest():
    with open(LATEST_LOG, 'r') as file:
        latest_log = json.load(file)
    latest_file = dict()
    file = dict()
    with tqdm.tqdm(total = len(latest_log.keys())) as bar:
        for name in latest_log.keys():
            ts = latest_log[name]['timestamp']
            if not ts in file:
                file[ts] = []
            file[ts].append(name)
            bar.update(1)
    with tqdm.tqdm(total = len(file.keys())) as bar:
        for ts in file.keys():
            path = os.path.join('.', 'hist', INDEX, str(ts) + '.json')
            with open(path, 'r') as fp:
                tmp = json.load(fp)
                for name in file[ts]:
                    latest_file[name] = tmp[name]
            bar.update(1)
    with open(LATEST_FILE, 'w') as file:
        json.dump(latest_file, file, sort_keys = True)

if __name__ == '__main__':
    print('[INFO] Crawling latest course info ...')
    ret = crawler.crawl(INDEX)
    print('[INFO] Comparing to the old version ...')
    write_update(ret[0], ret[1])
    print('[INFO] Writing the latest info ...')
    create_latest()
