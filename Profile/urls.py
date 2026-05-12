from django.contrib import admin
from django.urls import path
from .views import Profile_view

urlpatterns = [
   path('myprofile/',Profile_view.as_view(),name="profile")
]
