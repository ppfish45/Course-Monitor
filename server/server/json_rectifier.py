from django.http import JsonResponse

def get_error_json(err_msg):
    ret = dict()
    ret['error'] = True
    ret['errMsg'] = err_msg
    return JsonResponse(ret, status = 400)

def get_correct_json(data):
    ret = dict()
    ret['error'] = False
    ret['data'] = data
    return JsonResponse(ret)