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

def rideDetails(request, rideId):
    passengerId = request.COOKIES['id']
    if request.method == "POST":
        rideConfirmation = request.POST.get("wantToRide")
        if rideConfirmation == "yes":
            rideDictionary = getRideDetailsUsingRideId(rideId, passengerId)
            rideDetailsByRideId = RideDetails.objects.filter(rideId=rideId).first()
            rideDetailsByRideId.numberOfPassengersLeft -= 1
            rideDetailsByRideId.save()
            if rideDetailsByRideId.numberOfPassengersLeft != 0:
                newRide = RideDetails.objects.create(
                    numberOfPassengersLeft=0,
                    user_id=rideDictionary["userId"],
                    passenger=passengerId,
                    isSeatAvailable=False,
                    time=rideDictionary["time"],
                    date=rideDictionary["date"],
                    cost=rideDictionary["cost"]
                )
                newRide.save()
                newRideSourceDestinationDetails = RideSourceDestinationDetails.objects.create(
                    source=rideDictionary["source"],
                    destination=rideDictionary["destination"],
                    ride_id=newRide.rideId,
                    isRideAvailable=False)
                newRideSourceDestinationDetails.save()
            else:
                rideDetailsByRideId.passenger_id = passengerId
                rideDetailsByRideId.isSeatAvailable = False
                rideSourceDestinationDetails = RideSourceDestinationDetails.objects.filter(ride_id=rideId).first()
                rideSourceDestinationDetails.isRideAvailable = False
                rideSourceDestinationDetails.save()
                rideDetailsByRideId.save()
        return redirect("../../DashBoard/")
    try:
        rideDictionary = getRideDetailsUsingRideId(rideId, passengerId)
        return render(request, 'HTML/RideDetails.html', {"rideDetailsDictionary": rideDictionary})
    except:
        return redirect('../Error/')


def getRideDetailsUsingRideId(rideId, passengerId):
    rideDetailsByRideId = RideDetails.objects.filter(rideId=rideId).first()
    rideSourceDestinationDetails = RideSourceDestinationDetails.objects.filter(ride_id=rideId).first()
    user = User.objects.filter(userId=rideDetailsByRideId.user_id).first()
    presentRide = RideDetails.objects.filter(user_id=rideDetailsByRideId.user_id, passenger=passengerId).first()
    ownRide = RideDetails.objects.filter(user_id=passengerId, rideId=rideId).first()
    selected = False
    if presentRide is not None or ownRide is not None:
        selected = True
    rideDictionary = {
        "rideId": rideId,
        "source": rideSourceDestinationDetails.source,
        "destination": rideSourceDestinationDetails.destination,
        "name": user.name,
        "userId": user.userId,
        "numberOfPassengersLeft": rideDetailsByRideId.numberOfPassengersLeft,
        "date": rideDetailsByRideId.date,
        "time": rideDetailsByRideId.time,
        "cost": rideDetailsByRideId.cost,
        "selected": selected
    }
    return rideDictionary


def requestRide(request):
    placeholder = "Enter_the_Destination"
    isDestinationPresent = False
    if request.method == "POST":
        destinationSearch = request.POST.get('searchText')
        listOfRides = []
        if destinationSearch != '':
            placeholder = destinationSearch
            isDestinationPresent = True
            rideSourceDestinationDetails = RideSourceDestinationDetails.objects.filter(destination=destinationSearch)
            for i in rideSourceDestinationDetails:
                rideId = i.ride_id
                rideDetailsByRideId = RideDetails.objects.filter(rideId=rideId).first()
                if rideDetailsByRideId.isSeatAvailable:
                    numberOfPassengersLeft = rideDetailsByRideId.numberOfPassengersLeft
                    user = User.objects.filter(userId=rideDetailsByRideId.user_id).first()
                    listOfRides.append(
                        {"source": i.source,
                         "destination": destinationSearch,
                         "name": user.name,
                         "numberOfPassengersLeft": numberOfPassengersLeft,
                         "time": rideDetailsByRideId.time,
                         "date": rideDetailsByRideId.date,
                         "rideId": rideId
                         }
                    )
        return render(request, 'HTML/RequestRide.html',
                      {"isDestinationPresent": isDestinationPresent, "listOfRides": listOfRides,
                       "placeHolderValue": placeholder})
    return render(request, 'HTML/RequestRide.html',
                  {"placeHolderValue": placeholder, "isDestinationPresent": isDestinationPresent})


def driverDetails(request, userId):
    user = User.objects.filter(userId=userId).first()
    userDetails = {"name": user.name,"phoneNumber": user.phoneNumber}
    return render(request, "HTML/DriverDetails.html",{"userDetails":userDetails})