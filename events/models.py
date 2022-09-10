from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Event(models.Model):

    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null= True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    #date
    #photo
    #video
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering =['-updated', '-created']

    def __str__(self):
        return self.name

class Comment(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:50]