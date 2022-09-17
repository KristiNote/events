from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_page, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register_page, name="register"),
    path('', views.home, name='home'),
    path('event/<int:pk>/', views.get_event_details, name='event'),
    path('create-event/', views.create_event, name="create-event"),
    path('update-event/<int:pk>/', views.update_event, name="update-event"),
    path('delete-event/<int:pk>/', views.delete_event, name="delete-event"),
    path('delete-comment/<int:pk>/', views.delete_comment, name="delete-comment"),
    path('week-event', views.week_events, name="week-event"),
]