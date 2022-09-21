from django.contrib import admin
from embed_video.admin import AdminVideoMixin
from .models import Event, Topic, Comment


admin.site.register(Event)
admin.site.register(Topic)
admin.site.register(Comment)
