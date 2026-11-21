from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from urllib.parse import urlsplit

class SubdomainRoutingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = urlsplit(f"//{request.get_host()}").hostname    

        if (host == "app.zstars-ai.com" and request.path == "/"):
            if hasattr(request,'user') and request.user.is_authenticated:
                return redirect("dashboard")
            return redirect("iniciosesion")
        
        return None