from django.db import models
from django.conf import settings
from django.db.models import Sum


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Event(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='event/images/', null=True)
    seats = models.IntegerField(default=0)
    price = models.IntegerField(default=10)
    #video
    # ticket_available
    start_date = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def available_seats(self):
        sold = self.purchases.aggregate(Sum("quantity"))
        total = 0 if sold.get("quantity__sum") is None else sold.get("quantity__sum")
        return self.seats - total

    class Meta:
        ordering =['-updated', '-created']

    def __str__(self):
        return self.name


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.body[0:50]


class Purchase(models.Model):
    event = models.ForeignKey(Event, related_name="purchases", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    purchased_on = models.DateTimeField()

    class Meta:
        db_table = "purchases"
