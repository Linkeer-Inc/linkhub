from django.shortcuts import render

def landing_page(request):
    return render(request=request, template_name="index.html")

def custom_404(request, exception):
    print("opq")
    return render(request, "404.html", status=404)