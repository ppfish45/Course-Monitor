from django.http import JsonResponse

from . import settings_local

def add_cors_headers(func):
    def inner(*args, **kwargs):
        r = func(*args, **kwargs)
        for k, v in settings_local.cors_headers.items():
            r[k] = v
        for k, v in r.items():
            print(k, ':', v)
        return r
    return inner

@add_cors_headers
def get_error_json(err_msg):
    ret = dict()
    ret['error'] = True
    ret['errMsg'] = err_msg
    return JsonResponse(ret, status = 400)

@add_cors_headers
def get_correct_json(data):
    ret = dict()
    ret['error'] = False
    ret['data'] = data
    return JsonResponse(ret)