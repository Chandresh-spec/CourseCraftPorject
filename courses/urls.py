from django.contrib import admin
from django.urls import path
from .views import ListCourseView,CourseInfoView,PurchaseCourse,MylearningViews,IsEnrolledView
urlpatterns = [
   path('home/',ListCourseView.as_view()),
   path('info/<int:pk>/',CourseInfoView.as_view()),
   path('purchase-course/',PurchaseCourse.as_view()),
   path('myLearning/',MylearningViews.as_view()),
   path('is-enrolled/<int:course_id>/',IsEnrolledView.as_view()),
   
]
