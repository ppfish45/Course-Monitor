from django.http import JsonResponse
from . import retriever

sem_list = {
    'Spring 2019' : 1830
}

def get_error_json(err_msg):
    ret = dict()
    ret['error'] = True
    ret['errMsg'] = err_msg
    return JsonResponse(ret)

def semester(request):
    if request.GET:
        if 'semStr' in request.GET:
            if request.GET['semStr'] in sem_list:
                return retriever.get_sem_info(sem_list[request.GET['semStr']])
            else:
                return get_error_json('Incorrect semester name.')
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
            'section' in request.GET and \
            'startTime' in request.GET and \
            'endTime' in request.GET:
            return retriever.get_data(request.GET['semCode'], request.GET['courseCode'], request.GET['section'], request.GET['startTime'], request.GET['endTime'])
        else:
            return get_error_json('Parameter(s) missing.')
    else:
        return get_error_json('Please use GET method to get info.')