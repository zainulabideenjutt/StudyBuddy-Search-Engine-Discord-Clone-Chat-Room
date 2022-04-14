from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    name=models.CharField(max_length=200,null=True,blank=True)
    email=models.EmailField(unique=True,null=True,)
    bio=models.TextField(null=True,blank=True)

    avatar=models.ImageField(null=True,default='avatar.svg')
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants=models.ManyToManyField(User,related_name='participants',blank=True)
    created = models.DateTimeField(auto_now_add=True)
    Updated = models.DateTimeField(auto_now=True)

    class Meta :
        ordering=['-Updated','-created']

    def __str__(self):
        return self.name


class Message(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    Updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-Updated', '-created']

    def __str__(self):
        return self.body[0:50]
