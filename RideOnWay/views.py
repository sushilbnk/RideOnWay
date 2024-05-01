from django.shortcuts import render, redirect
from .models import User, RideDetails, RideSourceDestinationDetails, DriverReviews, DriverRating
from django.core.mail import EmailMessage
from django.template import loader



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
            response = redirect('../DashBoard/')
            response.set_cookie("id", user.userId)
            return response
        else:
            return redirect('../Error/')
    return render(request, 'HTML/register.html')


def errorPage(request):
    return render(request, 'HTML/Error.html')


def login(request):
    if request.method == "POST":
        email = request.POST.get("email").lower()
        if checkIfUserExists(email):
            password = request.POST.get("password")
            if checkPassword(password, email):
                user = User.objects.filter(email=email).first()
                response = redirect('../DashBoard/')
                response.set_cookie("id", user.userId)
                return response
            return redirect('../Error/')
    return render(request, 'HTML/login.html')


def DashBoard(request):
    return render(request, 'HTML/Dashboard.html')



def checkIfUserExists(email):
    user = User.objects.filter(email=email).first()
    return user is not None


def checkPassword(password, email):
    user = User.objects.filter(email=email).first()
    return user.password == password


def createRide(request):
    if request.method == "POST":
        userId = request.COOKIES['id']
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
            newRide = RideDetails.objects.create(
                numberOfPassengersLeft=0,
                user_id=rideDictionary["userId"],
                passenger=passengerId,
                isSeatAvailable=False,
                relatedRideId=rideId,
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

            if rideDetailsByRideId.numberOfPassengersLeft == 0:
                rideDetailsByRideId.isSeatAvailable = False
                rideSourceDestinationDetails = RideSourceDestinationDetails.objects.filter(ride_id=rideId).first()
                rideSourceDestinationDetails.isRideAvailable = False
                rideSourceDestinationDetails.save()
                rideDetailsByRideId.save()
                user = User.objects.filter(userId=rideDetailsByRideId.user_id).first()
                sendEmailToDriver(user.email, {"name": user.name,
                                               "source": rideDictionary["source"],
                                               "destination": rideDictionary["destination"],
                                               "time": rideDictionary["time"],
                                               "date": rideDictionary["date"]})
                # sendEmail to the driver saying the seats are full
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
    presentRide = RideDetails.objects.filter(user_id=rideDetailsByRideId.user_id, passenger=passengerId,
                                             rideId=rideId).first()
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
    isSourcePresent = False
    if request.method == "POST":
        destinationSearch = request.POST.get('searchText')
        sourceSearch = request.POST.get('sourceText')
        listOfRides = []
        if destinationSearch != '':
            placeholder = destinationSearch
            isDestinationPresent = True

        if sourceSearch != '':
            isSourcePresent = True

        if isDestinationPresent and isSourcePresent:
            rideSourceDestinationDetails = RideSourceDestinationDetails.objects.filter(
                destination=destinationSearch, source=sourceSearch)
        elif isDestinationPresent:
            rideSourceDestinationDetails = RideSourceDestinationDetails.objects.filter(destination=destinationSearch)
        elif isSourcePresent:
            rideSourceDestinationDetails = RideSourceDestinationDetails.objects.filter(source=sourceSearch)
        else:
            rideSourceDestinationDetails = []

        for i in rideSourceDestinationDetails:
            rideId = i.ride_id
            rideDetailsByRideId = RideDetails.objects.filter(rideId=rideId).first()

            if rideDetailsByRideId.isSeatAvailable and not rideDetailsByRideId.isRideEnded and not rideDetailsByRideId.isRideStarted:
                numberOfPassengersLeft = rideDetailsByRideId.numberOfPassengersLeft
                user = User.objects.filter(userId=rideDetailsByRideId.user_id).first()
                listOfRides.append({
                    "source": i.source,
                    "destination": i.destination,
                    "name": user.name,
                    "numberOfPassengersLeft": numberOfPassengersLeft,
                    "time": rideDetailsByRideId.time,
                    "date": rideDetailsByRideId.date,
                    "rideId": rideId
                })

        return render(request, 'HTML/RequestRide.html', {
            "isDestinationPresent": isDestinationPresent,
            "isSourcePresent": isSourcePresent,
            "listOfRides": listOfRides,
            "placeHolderValue": placeholder
        })

    return render(request, 'HTML/RequestRide.html', {
        "placeHolderValue": placeholder,
        "isDestinationPresent": isDestinationPresent,
        "isSourcePresent": isSourcePresent
    })

def MyRidesAsADriver(request):
    userId = request.COOKIES['id']
    myRides = RideDetails.objects.filter(user_id=userId, passenger=None)
    listOfRides = []
    for ride in myRides:
        myRideDetails = RideSourceDestinationDetails.objects.filter(ride_id=ride.rideId).first()
        passengerList = getPassengerList(userId, ride.rideId)
        isPassengerPresent = True
        if len(passengerList) == 0:
            isPassengerPresent = False

        listOfRides.append(
            {"source": myRideDetails.source,
             "destination": myRideDetails.destination,
             "time": ride.time,
             "date": ride.date,
             "rideId": ride.rideId,
             "isPassengerPresent": isPassengerPresent,
             "passengerList": passengerList
             }
        )

    isRidePresent = True
    if len(listOfRides) == 0:
        isRidePresent = False
    return render(request, "HTML/MyRidesAsDriver.html", {
        "listOfRides": listOfRides,
        "isRidePresent": isRidePresent,
    })


def MyRidesAsAPassenger(request):
    userId = request.COOKIES['id']
    myRides = RideDetails.objects.filter(passenger=userId)
    listOfRides = []
    for ride in myRides:
        myRideDetails = RideSourceDestinationDetails.objects.filter(ride_id=ride.rideId).first()
        driverProfile = User.objects.filter(userId=ride.user_id).first()
        listOfRides.append(
            {"source": myRideDetails.source,
             "destination": myRideDetails.destination,
             "time": ride.time,
             "date": ride.date,
             "rideId": ride.rideId,
             "driverName": driverProfile.name,
             "driverPhoneNumber": driverProfile.phoneNumber,
             "userId": driverProfile.userId
             }
        )
    isRidePresent = True
    if len(listOfRides) == 0:
        isRidePresent = False
    return render(request, "HTML/MyRidesAsPassenger.html", {
        "listOfRides": listOfRides,
        "isRidePresent": isRidePresent
    })


def driverDetails(request, userId):
    user = User.objects.filter(userId=userId).first()
    userRating = DriverRating.objects.filter(user_id=userId).first()
    isReviewPresent = True
    reviewList = []
    if userRating is None:
        isReviewPresent = False
        rating = 0
    else:
        rating = userRating.overallRating
        reviewList = getReviewList(userId)
    print(reviewList)
    userDetails = {"name": user.name, "phoneNumber": user.phoneNumber, "rating": rating}
    return render(request, "HTML/DriverDetails.html",
                  {"userDetails": userDetails, "isReviewPresent": isReviewPresent, "reviewList": reviewList})


def getReviewList(userId):
    reviewList = []
    driverReviews = DriverReviews.objects.filter(user_id=userId)
    for review in driverReviews:
        reviewList.append({"review": review.review, "rating": review.rating})
    return reviewList


def getPassengerList(userId, rideId):
    passengerRides = RideDetails.objects.filter(user_id=userId, relatedRideId=rideId)
    passengerList = []
    for ride in passengerRides:
        if ride.passenger is not None:
            passengerProfile = User.objects.filter(userId=ride.passenger).first()
            passengerList.append({"name": passengerProfile.name, "phoneNumber": passengerProfile.phoneNumber, "email": passengerProfile.email})
            # print(passengerProfile.name, passengerProfile.phoneNumber)

    return passengerList


def RideReview(request, rideId):
    rideDetailsForReview = RideDetails.objects.filter(rideId=rideId).first()
    user = User.objects.filter(userId=rideDetailsForReview.user_id).first()
    rideSourceDestinationDetails = RideSourceDestinationDetails.objects.filter(ride_id=rideId).first()
    passengerId = request.COOKIES["id"]
    if request.method == "POST":
        rating = request.POST.get("rating")
        review = request.POST.get("review")

        driverReview = DriverReviews.objects.create(
            review=review,
            user_id=user.userId,
            passengerId=passengerId,
            rideId=rideId,
            rating=rating)
        driverRating = DriverRating.objects.filter(user_id=user.userId).first()
        if driverRating is None:
            driverRating = DriverRating.objects.create(
                overallRating=rating,
                totalNumberOfRides=1,
                user_id=user.userId
            )
            driverRating.save()
        else:
            driverRating.overallRating = (driverRating.overallRating * driverRating.totalNumberOfRides + int(
                rating)) // (
                                                 driverRating.totalNumberOfRides + 1)
            driverRating.totalNumberOfRides += 1
            driverRating.save()

    rideReview = DriverReviews.objects.filter(passengerId=passengerId, rideId=rideId).first()
    isRideReviewGiven = False
    if rideReview is not None:
        isRideReviewGiven = True
    rideDetailsDictionary = {
        "name": user.name,
        "source": rideSourceDestinationDetails.source,
        "destination": rideSourceDestinationDetails.destination,
        "isRideReviewGiven": isRideReviewGiven,
        "rideId": rideId
    }
    return render(request, "HTML/RideReview.html", {"rideDetailsDictionary": rideDetailsDictionary})


def rideStartDetails(request, rideId):
    rideDetailsForStarting = RideDetails.objects.filter(rideId=rideId).first()
    rideSourceDestinationDetails = RideSourceDestinationDetails.objects.filter(ride_id=rideId).first()
    userId = request.COOKIES['id']
    user = User.objects.filter(userId=userId).first()

    if request.method == "POST":
        value = request.POST.get("wantToRide")
        if value == "yes|StartRide":
            rideDetailsForStarting.isRideStarted = True
            rideDetailsForStarting.save()
            emailList = []
            passengerList = getPassengerList(userId, rideId)
            for passenger in passengerList:
                emailList.append(passenger['email'])
            content = {"source": rideSourceDestinationDetails.source,
                       "destination": rideSourceDestinationDetails.destination,
                       "time": rideDetailsForStarting.time,
                       "date": rideDetailsForStarting.date,
                       "state": "Started"}
            sendEmailToPassengers(emailList, content)
        elif value == "yes|EndRide":
            rideDetailsForStarting.isRideEnded = True
            rideDetailsForStarting.save()
            passengerList = getPassengerList(userId, rideId)
            emailList = []
            for passenger in passengerList:
                emailList.append(passenger['email'])
            content ={ "source": rideSourceDestinationDetails.source,
                       "destination": rideSourceDestinationDetails.destination,
                       "time": rideDetailsForStarting.time,
                       "date": rideDetailsForStarting.date,
                       "state": "Ended"}
            sendEmailToPassengers(emailList, content)

        print(value)
        # sendEmail(EndRide and Start Ride to the passengers)
    rideDetailsDictionary = {
        "name": user.name,
        "source": rideSourceDestinationDetails.source,
        "destination": rideSourceDestinationDetails.destination,
        "started": rideDetailsForStarting.isRideStarted,
        "ended": rideDetailsForStarting.isRideEnded,
        "rideId": rideId,
        "date": rideDetailsForStarting.date,
        "time": rideDetailsForStarting.time,
        "numberOfPassengersLeft": rideDetailsForStarting.numberOfPassengersLeft
    }
    return render(request, 'HTML/RideStartDetails.html', {"rideDetailsDictionary": rideDetailsDictionary})


def sendEmailToDriver(emailId, content):
    template = loader.get_template('HTMl/EmailTemplate.html').render(content)
    print(template)
    email = EmailMessage(
        "The Ride is Full",
        template,
        #email
        [emailId]
    )
    email.content_subtype = 'html'
    result = email.send()
    return result


def sendEmailToPassengers(emailIdList, content):
    template = loader.get_template('HTMl/PassengersEmailTemplate.html').render(content)
    print(template)
    email = EmailMessage(
        ("The Ride has " + content['state']),
        template,
        #email
        emailIdList
    )
    email.content_subtype = 'html'
    result = email.send()
    return result



def home(request):
    return render(request, "HTML/Home.html")