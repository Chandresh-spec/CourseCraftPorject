from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    ROLE_CHOICE=(
        ('Students','student'),
        ('Admin','teacher'),
    )
    role=models.CharField(choices=ROLE_CHOICE,default='student',null=False,blank=False)
    mobile_number=models.CharField(max_length=12,null=True,blank=False)
