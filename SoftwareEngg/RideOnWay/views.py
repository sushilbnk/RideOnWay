from django.shortcuts import render, redirect
from .models import User



# This is register route

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



#This is the login route

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


def checkPassword(password, email):
    user = User.objects.filter(email=email).first()
    return user.password == password

def checkIfUserExists(email):
    user = User.objects.filter(email=email).first()
    print(user, user is not None)
    print(User.objects.all().values())
    return user is not None

def createRide(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if checkIfUserExists(email):
            user = User.objects.filter(email=email).first()
            userId = user.userId
            rideDetails = RideDetails.objects.create(
                numberOfPassengersLeft=request.POST.get('numberOfPassengers'),
                user_id=userId,
                passenger=None,
                isSeatAvailable=True,
                time=request.POST.get("time"),
                date=request.POST.get("date"),
                cost=request.POST.get("cost")
            )
            source = request.POST.get('source').lower()
            destination = request.POST.get('destination').lower()
            stop1 = request.POST.get('stop1').lower()
            stop2 = request.POST.get('stop2').lower()
            stop3 = request.POST.get('stop3').lower()
            stopList = [stop1, stop2, stop3]
            createRoutes(source, destination, stopList, rideDetails.rideId, rideDetails.isSeatAvailable)
            return redirect('../DashBoard/')
        else:
            return redirect('../Error/')
    return render(request, 'HTML/CreateRide.html')


def createRoutes(source, destination, stopList, rideId, isRideAvailable):
    RideSourceDestinationDetails.objects.create(
        source=source,
        destination=destination,
        ride_id=rideId,
        isRideAvailable=isRideAvailable
    )
    for i in range(len(stopList)):
        if stopList[i] != '':
            rideSourceDestinationDetails = RideSourceDestinationDetails.objects.create(
                source=source,
                destination=stopList[i],
                ride_id=rideId,
                isRideAvailable=isRideAvailable
            )
            rideSourceDestinationDetails.save()
            rideSourceDestinationDetails = RideSourceDestinationDetails.objects.create(
                source=stopList[i],
                destination=destination,
                ride_id=rideId,
                isRideAvailable=isRideAvailable
            )
            rideSourceDestinationDetails.save()
        for j in range(i + 1, len(stopList)):
            if stopList[i] != '' and stopList[j] != '':
                rideSourceDestinationDetails = RideSourceDestinationDetails.objects.create(
                    source=stopList[i],
                    destination=stopList[j],
                    ride_id=rideId,
                    isRideAvailable=isRideAvailable
                )
                rideSourceDestinationDetails.save()

