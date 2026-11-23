from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from urllib.parse import urlsplit
from games.views import redireccion_por_rol

class SubdomainRoutingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = urlsplit(f"//{request.get_host()}").hostname

        if host == "app.zstars-ai.com" and request.path == "/":
            if request.user.is_authenticated:
                return redireccion_por_rol(request.user)

            return redirect("iniciosesion")

        return None