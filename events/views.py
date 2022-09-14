from django import template
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Event, Topic, Comment
from .forms import EventForm


User = get_user_model()



def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does note exists")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Wrong Username or Password')

    context = {'login': login}
    return render(request, 'login_register.html', context)


def logout_user(request):
    logout(request)
    return redirect('home')


def register_page(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration!')

    return render(request, 'register.html', {'form': form})


def home(request):
    q = request.GET.get('q')

    events = Event.objects.all()
    if q is not None:
        events = events.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )

    topics = Topic.objects.all()
    event_count = events.count()

    try:
        page_no = int(request.GET.get("page", "1"))
    except ValueError:
        page_no = 1

    paginator = Paginator(events, per_page=2)
    page_obj = paginator.page(page_no)

    context = {'events': events, 'topics': topics, 'event_count': event_count}
    return render(request, 'home.html', context)


def get_event_details(request, pk):
    event = Event.objects.get(id=pk)
    event_comments = event.comment_set.all().order_by('-created')

    if request.method == 'POST':
        comment = Comment.objects.create(
            user=request.user,
            event=event,
            body=request.POST.get('body')
        )

    context = {'event': event, 'event_comments': event_comments}
    return render(request, 'event.html', context)


@permission_required("events.add_event")
def create_event(request):
    form = EventForm()

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    return render(request, "event_form.html", {'form': form})


@permission_required("events.change_event")
def update_event(request, pk):
    event = Event.objects.get(id=pk)
    form = EventForm(instance=event)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'event_form.html', context)


@permission_required("events.delete_event")
def delete_event(request, pk):
    event = Event.objects.get(id=pk)

    if request.method == 'POST':
        event.delete()
        return redirect('home')

    return render(request, 'delete.html', {'obj': event})


@login_required(login_url='login')
def delete_comment(request, pk):
    comment = Comment.objects.get(id=pk)

    if request.user != comment.user:
        return redirect('login')

    if request.method == 'POST':
        comment.delete()
        return redirect('home')

    return render(request, 'delete.html', {'obj': comment})


