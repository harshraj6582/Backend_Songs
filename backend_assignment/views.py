from django.shortcuts import render

def home(request):
    """Serve the main frontend page."""
    return render(request, 'index.html') 