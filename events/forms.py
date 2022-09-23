from django.forms import ModelForm, forms
from .models import Event, Contact


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields ='__all__'

class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'
