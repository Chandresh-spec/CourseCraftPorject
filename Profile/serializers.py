from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ProfileModel

User=get_user_model()


class Profile_Serializer(serializers.ModelSerializer):
    class Meta:
        model=ProfileModel
        fields=('user','email',"bio","profile_img")
    


    


        