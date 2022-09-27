from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func

def allowed_user(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            group=None
            if request.user.groups.exists():
                group=request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('คุณไม่ได้รับสิทธ์ในการเข้าถึงการจัดการระบบ')
        return wrapper_func
    return decorator

def only_admin(view_func):
    def wrapper_function(request, *args, **kwargs):
        group=None
        if request.user.groups.exists():
            group=request.user.groups.all()[0].name
            
        if group == 'commonuser':
            return redirect('frontdex')
        
        if group == 'votecreator':
            return redirect('frontdex')
        
        if group == 'admin':
            return view_func(request, *args, **kwargs)
    return wrapper_function