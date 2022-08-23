# chat/views.py
from django.shortcuts import render

def log(request):
    return render(request, 'log.html')