from . import views
from django.urls import path

urlpatterns = [
    path('', views.home),
    path('Register/', views.register),
    path('Login/', views.login),
    path('DashBoard/', views.DashBoard),
    path('Error/', views.errorPage),
    path('createRide/', views.createRide),
    path('requestRide/', views.requestRide),
    path('rideDetails/<rideId>/', views.rideDetails),
    path('DriverDetails/<userId>/', views.driverDetails),
    path('myRidesAsADriver/', views.MyRidesAsADriver),
    path('myRidesAsAPassenger/', views.MyRidesAsAPassenger),
    path('rideReview/<rideId>/', views.RideReview),
    # path('rideStart/<rideId>/', views.rideStartDetails)
]