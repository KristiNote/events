import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
import datetime
from django.conf import settings # new
from django.http.response import JsonResponse # new
from django.views.decorators.csrf import csrf_exempt # new
from django.views.generic.base import TemplateView

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
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')

    return render(request, "event_form.html", {'form': form})


@permission_required("events.change_event")
def update_event(request, pk):
    event = Event.objects.get(id=pk)
    form = EventForm(instance=event)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
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
        return redirect('event', pk=comment.event_id)

    return render(request, 'delete.html', {'obj': comment})



def week_events(request):
    date = datetime.date.today()
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(7)

    event_this_week = Event.objects.filter(start_date__range=[start_week, end_week])

    return render(request, 'events_of_week.html', {'event_this_week': event_this_week})


class HomePageView(TemplateView):
    template_name = 'home.html', 'event.html'

# new
@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def create_checkout_session(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    quantity = int(request.GET.get("quantity", "1"))
    if quantity > event.available_seats:
        return JsonResponse({"error": "Not that many seats available"}, status=400)

    if request.method == 'GET':
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - capture the payment later
            # [customer_email] - prefill the email input in the form
            # For full details see https://stripe.com/docs/api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'success/?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        "price_data": {
                            "currency": "eur",
                            "unit_amount": event.price * 100,
                            "product_data": {
                                "name": event.name,
                                "description": event.description,
                            },
                        },
                        "quantity": 1,
                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


def get_payment_success(request):
    return render(request, "events/payment_success.html")


def get_payment_cancel(request):
    return render(request, "events/payment_cancel.html")