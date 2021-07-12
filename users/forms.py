from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from .models import *


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username',
                  'email', 'password1', 'password2', 'groups']


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['alloted_time', 'meeting_link']


class MedecineForm(forms.ModelForm):
    class Meta:
        model = Medecine
        fields = ['name', 'detail']


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = '__all__'
        exclude = ['user']


class WorkingDaysForm(forms.ModelForm):
    class Meta:
        model = WorkingDays
        fields = ['day_name']


class TimeSlotsForm(forms.ModelForm):
    class Meta:
        model = TimeSlots
        fields = ['start_time', 'end_time', 'day']


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'
        exclude = ['user']


class SymptomForm(forms.ModelForm):
    class Meta:
        model = Symptom
        fields = ['name']

# ------------------------------------------------------------------
# pharmacy forms here


# class AddProduct(forms.Form):
#     product_name = forms.CharField(label='Product Name', max_length=100)
#     product_price = forms.FloatField(label='Product Price', required=True)
#     product_minquantity = forms.IntegerField(
#         label='Alert Quantity', required=True)
#     product_available = forms.IntegerField(
#         label='Available Quantity', required=True)
#     product_cp = forms.FloatField(label='cost price', required=True)
#     product_quantity = forms.CharField(
#         label='quantity of tablets/liquid in one unit', required=True, max_length=100)
#     product_drugs = forms.CharField(
#         label='drugs in medicine', required=True,  max_length=200)
#     product_brand = forms.CharField(
#         label='brand', required=True, max_length=100)

class AddProduct(forms.ModelForm):
    class Meta:
        model = specificproducts
        fields = '__all__'
        exclude = ['Pharmacist']

# pharmacy forms end
# ------------------------------------------------------------------


# -----------------------------------------------------------------
# pathology forms


class addpro(forms.ModelForm):
    class Meta:
        model = labtest
        fields = '__all__'
        exclude = ['Pathologist']


# pathology forms end
# -------------------------------------------------------------------
