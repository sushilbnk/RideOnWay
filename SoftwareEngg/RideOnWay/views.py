from django.shortcuts import render, redirect
from .models import User


# Create your views here.
def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not checkIfUserExists(email):
            password = request.POST.get("password")
            name = request.POST.get("name")
            phoneNumber = request.POST.get("phoneNumber")
            user = User.objects.create(
                email=email,
                password=password,
                phoneNumber=phoneNumber,
                name=name
            )
            user.save()
            return redirect('../DashBoard/')
        else:
            return redirect('../Error/')
    return render(request, 'HTML/register.html')

def errorPage(request):
    return render(request, 'HTML/Error.html')

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if checkIfUserExists(email):
            password = request.POST.get("password")
            if checkPassword(password, email):
                return redirect('../DashBoard/')
            return redirect('../Error/')
    return render(request, 'HTML/login.html')


def DashBoard(request):
    return render(request, 'HTML/Dashboard.html')


def checkIfUserExists(email):
    user = User.objects.filter(email=email).first()
    print(user, user is not None)
    print(User.objects.all().values())
    return user is not None


def checkPassword(password, email):
    user = User.objects.filter(email=email).first()
    return user.password == password
