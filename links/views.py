from django.shortcuts import render

def links(request):
    return render(request=request, template_name="links.html")
