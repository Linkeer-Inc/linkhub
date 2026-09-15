from django.shortcuts import render
from django.http import StreamingHttpResponse, Http404, HttpResponse

from vercel.blob import get

def landing_page(request):
    return render(request=request, template_name="index.html")

def serve_private_blob(request, pathname):
    result = get(pathname, access="private")
    
    if result is None:
        raise Http404
    return HttpResponse(
        result.content,
        content_type=result.content_type,
        headers={"Cache-Control": "private, no-cache"},
    )

def custom_404(request, exception):
    return render(request, "404.html", status=404)