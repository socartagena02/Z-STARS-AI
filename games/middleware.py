from django.shortcuts import redirect

class SubdomainRoutingMiddware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        host = request.get_host().split(":")[0].lower()
        
        if (host == "app.zstars-ai.com" and request.path == "/"):
            if request.user.is_authenticated:
                return redirect("dashboard")
            return redirect("iniciosesion")
        return self.get_response(request)