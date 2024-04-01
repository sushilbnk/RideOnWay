from django.db import models

#Model Creation
class User(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=10)
    phoneNumber = models.CharField(max_length=10)
    name = models.CharField(max_length=150)
    userId = models.AutoField(primary_key=True)
    
class RideDetails(models.Model):
    rideId = models.AutoField(primary_key=True)
    numberOfPassengersLeft = models.IntegerField()
    user = models.ForeignKey(User, to_field='userId', on_delete=models.CASCADE)
    passenger = models.IntegerField(null=True)
    isSeatAvailable = models.BooleanField()
    time = models.CharField(max_length=20, null=True)
    date = models.CharField(max_length=100, null=True)
    cost = models.IntegerField(default=0)


class RideSourceDestinationDetails(models.Model):
    source = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    sourceDestinationId = models.AutoField(primary_key=True)
    ride = models.ForeignKey(RideDetails, to_field='rideId', on_delete=models.CASCADE)
    isRideAvailable = models.BooleanField()
