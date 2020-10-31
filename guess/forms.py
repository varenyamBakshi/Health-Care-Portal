from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm



class guessform(forms.Form):
    symptoms = forms.CharField(label='Symptoms', max_length=1000)
    