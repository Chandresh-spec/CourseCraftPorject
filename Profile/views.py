from django.shortcuts import render
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from .serializers import Profile_Serializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser,FormParser,JSONParser
User=get_user_model()

# Create your views here.




class Profile_view(APIView):
    parser_classes=[MultiPartParser,FormParser,JSONParser]
    
    def get(self,request):

        
        serializer=Profile_Serializer(request.user.profile)
    
        return Response({
            "status":True,
            "result":serializer.data
        },status=status.HTTP_200_OK)
    

    def patch(self,request):
        profile=request.user.profile
        serializer=Profile_Serializer(profile,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

       

        return Response({
            "status":True,
            "message":"Profile Modified Sucessfully"
        },status=status.HTTP_202_ACCEPTED)




