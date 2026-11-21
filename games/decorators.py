from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from games.models import Perfiles

def requiere_rol(*roles):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            perfil = Perfiles.objects.filter(user=request.user).first()

            if perfil is None or perfil.rol not in roles:
                return redirect("home")

            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator