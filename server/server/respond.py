from . import retriever

from server.json_rectifier import get_correct_json
from server.json_rectifier import get_error_json

sem_list = [
    {
        'name' : 'Spring 2019',
        'semCode' : 1830 
    },
    {
        'name' : 'Summer 2019',
        'semCode' : 1840
    }
]

def default(request):
    return get_correct_json(sem_list)

def semester(request):
    if request.GET:
        if 'semCode' in request.GET:
            return retriever.get_sem_info(request.GET['semCode'])
        else:
            return get_error_json('Parameter(s) missing.')
    else:
        return get_error_json('Please use GET method to get info.')

def course(request):
    if request.GET:
        if 'semCode' in request.GET and \
            'courseCode' in request.GET:
            return retriever.get_course_section(request.GET['semCode'], request.GET['courseCode'])
        else:
            return get_error_json('Parameter(s) missing.')
    else:
        return get_error_json('Please use GET method to get info.')

def section(request):
    if request.GET:
        if 'semCode' in request.GET and \
            'courseCode' in request.GET and \
            'section' in request.GET:
            args = [
                request.GET['semCode'],
                request.GET['courseCode'],
                request.GET['section'],
                request.GET['startTime'] if 'startTime' in request.GET else -1,
                request.GET['endTime'] if 'endTime' in request.GET else -1,
                ]
            return retriever.get_data(*args)
        else:
            return get_error_json('Parameter(s) missing.')
    else:
        return get_error_json('Please use GET method to get info.')