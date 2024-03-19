from django.shortcuts import render
from .models import User


# Create your views here.
def register(request):
    return render(request, 'HTML/register.html')


def login(request):
    return render(request, 'HTML/login.html')
