from django.db import models
from django.contrib.auth import get_user_model

User=get_user_model()
# Create your models here.

class Courses(models.Model):
    LEVEL_CHOICES=(
        ('beginner','Beginner'),
        ('intermediate','Intermedaite'),
        ('advanced','Advanced'),
    )
    course_name=models.CharField(max_length=100,null=False,blank=False)
    price=models.DecimalField(max_digits=8,decimal_places=2)

    duration=models.IntegerField()
    certificate=models.BooleanField(default=True)

    course_img=models.ImageField(upload_to='course_img',null=True,blank=True)
    short_description=models.CharField(max_length=150)

    description=models.TextField()
    levels=models.CharField(max_length=20,choices=LEVEL_CHOICES)

    
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)

    instructor_name=models.CharField(max_length=100)
    total_students=models.PositiveIntegerField(default=0)
    rating=models.DecimalField(max_digits=2,decimal_places=1,default=0.0)


    def __str__(self):
        return  self.course_name
    






class UserCoursePurchase(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    course=models.ForeignKey(Courses,on_delete=models.CASCADE)
    is_paid=models.BooleanField(default=False)
    purchased_at=models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together=('user','course')

    
    def __str__(self):
        return f"{self.user.username} -> {self.course.course_name}"
