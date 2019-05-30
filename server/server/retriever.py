import os
import sys
import json
import fcntl
import bisect

from django.http import JsonResponse
from django.http import HttpResponse

from server.json_rectifier import get_correct_json
from server.json_rectifier import get_error_json

data_path = os.path.abspath(os.path.join(os.path.realpath(__file__), '..', '..', '..'))
index_path = os.path.join(data_path, 'index')

def get_sem_info(sem_code):
    file_path = os.path.join(index_path, str(sem_code), 'info.json')
    if not os.path.exists(file_path):
        return get_error_json('Semester does not exist.')
    try:
        with open(file_path, 'r') as file:
            fcntl.flock(file.fileno(), fcntl.LOCK_SH)
            ret = json.load(file)
            return get_correct_json(ret)
    except:
        return get_error_json('File error.')

def get_course_section(sem_code, course_code):
    file_name = course_code + '.json'
    file_path = os.path.join(index_path, sem_code, 'courses', file_name)
    if not os.path.exists(file_path):
        return get_error_json('Course does not exist.')
    try:
        with open(file_path, 'r') as file:
            fcntl.flock(file.fileno(), fcntl.LOCK_SH)
            data = json.load(file)
            ret = list(data.keys())
            return get_correct_json(ret)
    except:
        return get_error_json('File error.')

def get_data(sem_code, course_code, section_str, start_time, end_time):
    file_name = course_code + '.json'
    file_path = os.path.join(index_path, sem_code, 'courses', file_name)
    if not os.path.exists(file_path):
        return get_error_json('Course does not exist.')
    print(section_str)
    try:   
        with open(file_path, 'r') as file:
            fcntl.flock(file.fileno(), fcntl.LOCK_SH)
            data = json.load(file)
            ret = data[section_str]
            time_list = [x['timestamp'] for x in ret]
            if start_time == -1:
                left = 0
            else:
                left = bisect.bisect_left(time_list, int(start_time), 0, len(time_list))
            if end_time == -1:
                righ = len(ret)
            else:
                righ = bisect.bisect_right(time_list, int(end_time), 0, len(time_list))
            ret = ret[left : righ]
            return get_correct_json(ret)
    except:
            return get_error_json('File error.')
