from django.shortcuts import render
from .serializers import CourseSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin,RetrieveModelMixin,CreateModelMixin
from .models import Courses,UserCoursePurchase
from .serializers import CourseSerializer,CPISerializer,MyLearningSerializers,ShowCoursesSerializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .pagination import CoursePagination
from django.core.cache import cache
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.




class ListCourseView(ListModelMixin,GenericAPIView):
    permission_classes=[AllowAny]
    queryset=Courses.objects.all()
    serializer_class=CourseSerializer
    pagination_class=CoursePagination
    filter_backends=[SearchFilter]
    search_fields=[
         'course_name',
         'short_description',
         'price',
    ]

   

    def get(self,request,*args,**kwargs):
        return self.list(request,*args,**kwargs)



class CourseInfoView(RetrieveModelMixin,GenericAPIView):
    queryset=Courses.objects.all()
    serializer_class=CourseSerializer
    def get(self, request, *args, **kwargs):
        return self.retrieve(request,*args,**kwargs)
    



class PurchaseCourse(CreateModelMixin,GenericAPIView):
        serializer_class=CPISerializer


        def perform_create(self, serializer):
            serializer.save(user=self.request.user)
        

        def post(self,request,*args,**kwargs):
             return self.create(request,*args,**kwargs)
    



class MylearningViews(ListModelMixin,GenericAPIView):
     serializer_class=MyLearningSerializers


     def get_queryset(self):
          return(UserCoursePurchase.objects.filter(user=self.request.user))
     

     def get(self,request,*args,**kwargs):
          return self.list(request,*args,**kwargs)


class IsEnrolledView(APIView):
    """
    GET /course/is-enrolled/<course_id>/
    Returns {"enrolled": true} if the logged-in user has purchased the course.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        enrolled = UserCoursePurchase.objects.filter(
            user=request.user,
            course_id=course_id
        ).exists()
        return Response({"enrolled": enrolled})

          
          

    