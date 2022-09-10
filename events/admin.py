from django.contrib import admin

from .models import Event, Topic, Comment, User

# Register your models here.


admin.site.register(Event)
admin.site.register(Topic)
admin.site.register(Comment)
