from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
User=get_user_model()

class ProfileModel(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    email=models.EmailField(null=False,blank=False)
    bio=models.CharField(max_length=100,default="hii everyone")
    profile_img=models.ImageField(upload_to='profile_img',null=True,blank=True)


    def __str__(self):
        return self.user.username
    




