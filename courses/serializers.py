from rest_framework import serializers
from .models import Courses,UserCoursePurchase



class CourseSerializer(serializers.ModelSerializer):
    course_img=serializers.ImageField(use_url=True)
    class Meta:
        model=Courses
        fields=('id','course_name','price','duration','certificate','course_img','short_description','description','levels',
                'instructor_name','total_students','rating')
        

        


    

class CPISerializer(serializers.ModelSerializer):
    class Meta:
        model=UserCoursePurchase
        fields= ["course"]
        read_only_fields=['is_paid','purchased_at']



class MyLearningSerializers(serializers.ModelSerializer):
    course=CourseSerializer(read_only=True)
    class Meta:
        model=UserCoursePurchase
        fields=['course']
        read_only_fields=['is_paid','purchased_at']





class ShowCoursesSerializers(serializers.ModelSerializer):
    class Meta:
        model=Courses
        fields=('id','course_name','price','duration','certificate','short_description','description','levels',
                'instructor_name','total_students','rating')
        
