

from . import views
from django.contrib import admin
from django.urls import path

# Defining required url patterns

urlpatterns = [
    path('Register/', views.register),
    path('Login/', views.login),
    path('DashBoard/', views.DashBoard),
    path('Error/', views.errorPage)
]
