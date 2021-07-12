from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from .models import *
from .filters import *
from .forms import *
from .models import *
from django.conf import settings
from django.http import JsonResponse
from django.views.generic import ListView
import os
import json
import numpy as np
import joblib
import pandas as pd
import requests
from django.http import HttpResponse
from django.views import View
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
import bs4


def signupUser(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            groupName = str(form.cleaned_data.get('groups')[0])
            group = Group.objects.get(name=groupName)
            user.groups.add(group)
            if groupName == 'doctor':
                Doctor.objects.create(user=user)
            elif groupName == 'patient':
                Patient.objects.create(user=user)
            elif groupName == 'pharmacist':
                Pharmacist.objects.create(user=user)
            else:
                Pathologist.objects.create(user=user)
            messages.success(request, 'user succesfully created')
            return redirect('loginUser')

    context = {'form': form}
    return render(request, 'signup.html', context)


def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'logged in')
            groupName = request.user.groups.all()[0].name
            return redirect(f'{groupName}Dashboard')
        else:
            messages.info(request, "Invalid credentials")
    context = {}
    return render(request, 'login.html', context)


def doctorProfileUpdate(request):
    user = request.user
    doctor = Doctor.objects.get(user=user)
    workingDays = WorkingDays.objects.filter(doctor=doctor)
    print(workingDays)
    doctorForm = DoctorForm(request.POST or None, instance=doctor)
    if 'submitDoctorForm' in request.POST:
        if doctorForm.is_valid():
            doctorForm.save()
    workingDaysForm = WorkingDaysForm(request.POST or None)
    if 'submitWorkingDayForm' in request.POST:
        if workingDaysForm.is_valid():
            temp = workingDaysForm.save()
            temp.doctor = doctor
            temp.save()
            doctorForm = DoctorForm(None, instance=doctor)
    slots = {}
    slots['Monday'] = []
    slots['Tuesday'] = []
    slots['Wednesday'] = []
    slots['Thursday'] = []
    slots['Friday'] = []
    slots['Saturday'] = []
    slots['Sunday'] = []
    for i in workingDays:
        j = TimeSlots.objects.filter(day=i)
        slots[i.day_name] = j
    timeSlotsForm = TimeSlotsForm(request.POST or None)
    if 'submitTimeSlotsForm' in request.POST:
        if timeSlotsForm.is_valid():
            timeSlotsForm.save()
            doctorForm = DoctorForm(None, instance=doctor)
    context = {'timeSlotsForm': TimeSlotsForm, 'monday': slots['Monday'], 'tuesday': slots['Tuesday'], 'wednesday': slots['Wednesday'], 'thursday': slots['Thursday'],
               'friday': slots['Friday'], 'saturday': slots['Saturday'], 'sunday': slots['Sunday'], 'workingDaysForm': workingDaysForm, 'doctorForm': doctorForm, 'workingDays': workingDays}
    return render(request, 'doctor/doctorProfileUpdate.html', context)


def patientProfileUpdate(request):
    user = request.user
    patient = Patient.objects.get(user=user)
    form = PatientForm(request.POST or None, instance=patient)
    if form.is_valid():
        form.save()
    context = {'form': form}
    return render(request, 'patientProfileUpdate.html', context)


def logoutUser(request):
    logout(request)
    messages.success(request, 'logged out')
    return redirect('loginUser')


def home(request):
    context = {}
    return render(request, 'home.html', context)


def doctorDashboard(request):
    context = {}
    return render(request, 'doctor/doctorDashboard.html', context)


def patientDashboard(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')

    r = requests.get('https://get.geojs.io/')
    ip_request = requests.get('https://get.geojs.io/v1/ip.json')
    ipAdd = ip_request.json()['ip']
    url = 'https://get.geojs.io/v1/ip/geo/'+ipAdd+'.json'
    geo_request = requests.get(url)
    geo_data = geo_request.json()
    print(geo_data['city'])
    mycity = geo_data['city']

    doctors = Doctor.objects.all()
    myFilter = DoctorFilter(request.GET, queryset=doctors)
    doctors = myFilter.qs
    print(request.GET.get("city"))
    inputCity = request.GET.get("city")
    if(inputCity == None or inputCity == ""):
        doctors = doctors.filter(city=mycity)
        inputCity = mycity
    saareDoctor = []
    for d in doctors:
        ekDoctor = []
        wd = WorkingDays.objects.filter(doctor=d)
        ekDoctor.append(d.user.id)
        for day in wd:
            l = []
            l.append(day)
            ts = TimeSlots.objects.filter(day=day)
            for time in ts:
                l.append(time)
            ekDoctor.append(l)
        saareDoctor.append(ekDoctor)
    # print(saareDoctor[0])
    context = {'myFilter': myFilter, 'doctors': doctors,
               'city': inputCity, 'saareDoctor': saareDoctor}
    return render(request, 'patientDashboard.html', context)


def bookAppointment(request, pk, pk2, pk3):
    print(pk)
    print(pk2)
    print(pk3)
    user = User.objects.get(id=pk)
    doctor = Doctor.objects.get(user=user)
    user = request.user
    patient = Patient.objects.get(user=user)
    wd = WorkingDays.objects.get(doctor=doctor, day_name=pk2)
    print(wd)
    ts = TimeSlots.objects.get(day=wd, start_time=pk3)
    print(ts.end_time)
    # print(user.username)
    # print(doctor.speciality)
    # print(patient)
    if request.method == 'POST':
        Appointment.objects.create(
            doctor=doctor, patient=patient, time_slot=ts)
        ts.occupied = True
        ts.save()
        return redirect('patientDashboard')
    context = {}
    return render(request, 'bookAppointment.html', context)


def myprescriptions(request):
    user = request.user
    patient = Patient.objects.get(user=user)
    appointments = patient.appointment_set.all()
    meds = Medecine.objects.all()
    context = {
        'appointments': appointments,
        'meds': meds,
    }

    return render(request, 'myprescriptions.html', context)


def patientAppointments(request):
    user = request.user
    patient = Patient.objects.get(user=user)
    print(patient.appointment_set.all())
    appointments = patient.appointment_set.all()
    context = {'appointments': appointments}
    return render(request, 'patientAppointments.html', context)


def doctorAppointments(request):
    user = request.user
    doctor = Doctor.objects.get(user=user)
    print(doctor.appointment_set.all())
    appointments = doctor.appointment_set.all()
    context = {'appointments': appointments}
    return render(request, 'doctor/doctorAppointments.html', context)


def appointmentMedsdoc(request, pk):
    appointment = Appointment.objects.get(id=pk)
    print(appointment.medecine_set.all())
    appointmentMeds = appointment.medecine_set.all()
    appointmentSymptoms = appointment.symptom_set.all()
    form = SymptomForm()
    cls = joblib.load('decision_tree.joblib')  # classification model

    symp_list = pd.read_csv('test_data.csv').columns[:-1]
    d = np.zeros((len(symp_list)))
    test_case = pd.DataFrame(d).transpose()
    test_case.columns = symp_list
    for symp in appointmentSymptoms:
        # print(symp.name)
        if symp.name in symp_list:
            test_case.loc[0, [symp.name]] = 1
    disease = cls.predict(test_case)
    url = syslink(disease)
    # print(disease[0])

    if request.method == 'POST':
        form = SymptomForm(request.POST)
        if form.is_valid():
            medi = form.save()
            medi.appointment = appointment
            medi.save()
            return redirect('appointmentMedsdoc', pk=pk)
    context = {
        'meds': appointmentMeds,
        'appointment': appointment,
        'symptoms': appointmentSymptoms,
        'form': form,
        'disease': disease[0],
        'pk': pk,
        'url':url,
    }
    return render(request, 'doctor/appointmentMeds.html', context)

def syslink(disease):
    res =  requests.get('https://google.com/search?q='+''.join(disease))
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    linkElements = soup.select('div#main > div > div > div > a')
    linkToOpen = min(1, len(linkElements))
    #print(linkElements[0].get('href'))
    return 'http://google.com'+linkElements[0].get('href')

def appointmentMeds(request, pk):
    appointment = Appointment.objects.get(id=pk)
    print(appointment.medecine_set.all())
    appointmentMeds = appointment.medecine_set.all()
    appointmentSymptoms = appointment.symptom_set.all()
    form = SymptomForm()
    cls = joblib.load('decision_tree.joblib')  # classification model

    symp_list = pd.read_csv('test_data.csv').columns[:-1]
    d = np.zeros((len(symp_list)))
    test_case = pd.DataFrame(d).transpose()
    test_case.columns = symp_list
    for symp in appointmentSymptoms:
        # print(symp.name)
        if symp.name in symp_list:
            test_case.loc[0, [symp.name]] = 1
    disease = cls.predict(test_case)
    url = syslink(disease)
    # print(disease[0])

    if request.method == 'POST':
        form = SymptomForm(request.POST)
        if form.is_valid():
            medi = form.save()
            medi.appointment = appointment
            medi.save()
            return redirect('appointmentMeds', pk=pk)
    context = {
        'meds': appointmentMeds,
        'appointment': appointment,
        'symptoms': appointmentSymptoms,
        'form': form,
        'disease': disease[0],
        'url':url,
    }
    return render(request, 'appointmentMeds.html', context)


def guessDisease(request, pk):
    appointment = Appointment.objects.get(id=pk)
    print(appointment.symptom_set.all())
    appointmentSymptoms = appointment.symptom_set.all()
    cls = joblib.load('decision_tree.joblib')  # classification model

    symp_list = pd.read_csv('test_data.csv').columns[:-1]
    d = np.zeros((len(symp_list)))
    test_case = pd.DataFrame(d).transpose()
    test_case.columns = symp_list
    for symp in appointmentSymptoms:
        print(symp.name)
        if symp.name in symp_list:
            test_case.loc[0, [symp.name]] = 1
    disease = cls.predict(test_case)
    print(disease[0])
    context = {'disease': disease[0],
               'symptoms': appointmentSymptoms, 'pk': pk}
    return render(request, 'guessDisease.html', context)


def updateAppointmentSymptoms(request, pk):
    appointment = Appointment.objects.get(id=pk)
    print(appointment)
    appointmentSymptoms = appointment.symptom_set.all()
    form = SymptomForm()
    if request.method == 'POST':
        form = SymptomForm(request.POST)
        if form.is_valid():
            medi = form.save()
            medi.appointment = appointment
            medi.save()
            return redirect('appointmentSymptoms', pk=pk)
    context = {'form': form, 'meds': appointmentSymptoms}
    return render(request, 'updateAppointmentSymptoms.html', context)


def appointmentSymptoms(request, pk):
    appointment = Appointment.objects.get(id=pk)
    print(appointment.symptom_set.all())
    appointmentSymptoms = appointment.symptom_set.all()
    context = {'symptoms': appointmentSymptoms, 'pk': pk}
    return render(request, 'appointmentSymptoms.html', context)


def updateAppointment(request, pk):
    appointment = Appointment.objects.get(id=pk)
    form = AppointmentForm(request.POST or None, instance=appointment)
    if form.is_valid():
        form.save()
        return redirect('appointmentMedsdoc', pk)
    context = {'form': form, 'pk': pk}
    return render(request, 'doctor/updateAppointment.html', context)


def updateAppointmentMeds(request, pk):
    appointment = Appointment.objects.get(id=pk)
    print(appointment)
    appointmentMeds = appointment.medecine_set.all()
    form = MedecineForm()
    if request.method == 'POST':
        form = MedecineForm(request.POST)
        if form.is_valid():
            medi = form.save()
            # form.save()
            # print(form.save.appointment)
            medi.appointment = appointment
            # print(meds.appointment)
            medi.save()
            return redirect('appointmentMedsdoc', pk)
    context = {'form': form, 'meds': appointmentMeds}
    return render(request, 'updateAppointmentMeds.html', context)

# ----------------------------------------------------------------------------
# pharmacy material here


def addproduct(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')

    customer = request.user.pharmacist
    order, created = WalkinOrder.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_cart_items
    groupname = str(request.user.groups.all()[0].name)
    name = request.user.first_name
    pharmacy = request.user.pharmacist
    pharmaname = request.user.pharmacist.PharmaName
    pharmacyid = request.user.pharmacist.id

    form = AddProduct()
    if request.method == 'POST':
        form = AddProduct(request.POST, request.FILES)
        if form.is_valid():
            newform = form.save(commit=False)
            newform.Pharmacist = pharmacy
            newform.save()
            return redirect('stock')

    context = {
        'form': form,
        'name': name,
        'groupname': groupname,
        'ordercount': ordercount,
    }
    return render(request, 'pharmacy/addproduct.html', context)


def pharmacistDashboard(request):
    customer = request.user.pharmacist
    order, created = WalkinOrder.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_cart_items
    groupname = str(request.user.groups.all()[0].name)
    name = request.user.first_name
    pharmacy = request.user.pharmacist
    pharmaname = request.user.pharmacist.PharmaName
    pharmacyid = request.user.pharmacist.id
    products = specificproducts.objects.filter(Pharmacist=pharmacy)
    if not request.user.is_authenticated:
        return redirect('loginUser')

    # doctors = Doctor.objects.all()
    myFilter = ProductFilter(request.GET, queryset=products)
    products = myFilter.qs
    # context = {'myFilter': myFilter, 'doctors': doctors}
    context = {
        'name': name,
        'myFilter': myFilter,
        'groupname': groupname,
        'products': products,
        'ordercount': ordercount,
    }
    return render(request, 'pharmacy/pharmacistdashboard.html', context)


def alertproducts(request):
    customer = request.user.pharmacist
    order, created = WalkinOrder.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_cart_items
    groupname = str(request.user.groups.all()[0].name)
    name = request.user.first_name
    pharmacy = request.user.pharmacist
    pharmaname = request.user.pharmacist.PharmaName
    pharmacyid = request.user.pharmacist.id
    products = specificproducts.objects.filter(Pharmacist=pharmacy)
    if not request.user.is_authenticated:
        return redirect('loginUser')
    context = {
        'name': name,
        'groupname': groupname,
        'products': products,
        'ordercount': ordercount,
    }
    return render(request, 'pharmacy/alertproduct.html', context)


def cart(request):
    name = request.user.first_name
    groupname = str(request.user.groups.all()[0].name)
    customer = request.user.patient
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_cart_items
    items = order.cart_set.all()
    if not request.user.is_authenticated:
        return redirect('loginUser')
    context = {
        'name': name,
        'groupname': groupname,
        'items': items,
        'order': order,
        'ordercount': ordercount,
    }
    return render(request, 'pharmacy/cart.html', context)


def stock(request):
    name = request.user.first_name
    groupname = str(request.user.groups.all()[0].name)
    if not request.user.is_authenticated:
        return redirect('loginUser')
    customer = request.user.pharmacist
    order, created = WalkinOrder.objects.get_or_create(
        customer=customer, complete=False)
    items = order.walkincart_set.all()
    ordercount = order.get_cart_items
    products = specificproducts.objects.filter(Pharmacist=customer)
    myFilter = StockFilter(request.GET, queryset=products)
    products = myFilter.qs
    context = {
        'name': name,
        'myFilter': myFilter,
        'groupname': groupname,
        'items': items,
        'ordercount': ordercount,
        'products': products,
    }
    return render(request, 'pharmacy/pharmacyallitems.html', context)


def walkincart(request):
    name = request.user.first_name
    groupname = str(request.user.groups.all()[0].name)
    customer = request.user.pharmacist
    order, created = WalkinOrder.objects.get_or_create(
        customer=customer, complete=False)
    items = order.walkincart_set.all()
    ordercount = order.get_cart_items
    if not request.user.is_authenticated:
        return redirect('loginUser')
    context = {
        'name': name,
        'groupname': groupname,
        'items': items,
        'order': order,
        'ordercount': ordercount,
    }
    return render(request, 'pharmacy/pharmacistcart.html', context)


def pinandbuypharmacy(request, pid):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    customer = request.user.patient
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_cart_items
    groupname = str(request.user.groups.all()[0].name)
    name = request.user.first_name
    pharmacies = Pharmacist.objects.all()
    appointment = Appointment.objects.get(id=pid)
    prescriptionmedicine = appointment.medecine_set.all()
    pinandbuy = True

    r = requests.get('https://get.geojs.io/')
    ip_request = requests.get('https://get.geojs.io/v1/ip.json')
    ipAdd = ip_request.json()['ip']
    url = 'https://get.geojs.io/v1/ip/geo/'+ipAdd+'.json'
    geo_request = requests.get(url)
    geo_data = geo_request.json()
    print(geo_data['city'])
    mycity = geo_data['city']
    print(mycity)
    pharmacies = pharmacies.filter(PharmaAddress=mycity)

    context = {
        'name': name,
        'groupname': groupname,
        'pharmacies': pharmacies,
        'ordercount': ordercount,
        'pinandbuy': pinandbuy,
        'prescriptionmedicine': prescriptionmedicine,
        'pid': pid,
    }
    return render(request, 'pharmacy/pharmacy.html', context)


def pharmacy(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    customer = request.user.patient
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_cart_items
    groupname = str(request.user.groups.all()[0].name)
    name = request.user.first_name
    pharmacies = Pharmacist.objects.all()
    r = requests.get('https://get.geojs.io/')
    ip_request = requests.get('https://get.geojs.io/v1/ip.json')
    ipAdd = ip_request.json()['ip']
    url = 'https://get.geojs.io/v1/ip/geo/'+ipAdd+'.json'
    geo_request = requests.get(url)
    geo_data = geo_request.json()
    print(geo_data['city'])
    mycity = geo_data['city']
    print(mycity)
    pharmacies = pharmacies.filter(PharmaAddress=mycity)
    pinandbuy = False

    context = {
        'name': name,
        'groupname': groupname,
        'pharmacies': pharmacies,
        'ordercount': ordercount,
        'pinandbuy': pinandbuy,
    }
    return render(request, 'pharmacy/pharmacy.html', context)


def pinandbuystore(request, pharmacyid, pid):
    customer = request.user.patient
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    name = request.user.first_name
    pharmacy = Pharmacist.objects.get(id=pharmacyid)
    groupname = str(request.user.groups.all()[0].name)
    items = order.cart_set.all()
    pinandbuy = True
    print(items)
    appointment = Appointment.objects.get(id=pid)
    prescriptionmedicine = appointment.medecine_set.all()
    alert = False

    for item in items:
        if item.product.Pharmacist != pharmacy:
            order.delete()
            alert = True
            break

    products = specificproducts.objects.filter(Pharmacist=pharmacy)
    ordercount = order.get_cart_items
    myFilter = ProductFilter(request.GET, queryset=products)
    products = myFilter.qs
    if not request.user.is_authenticated:
        return redirect('loginUser')
    context = {
        'name': name,
        'products': products,
        'groupname': groupname,
        'ordercount': ordercount,
        'alert': alert,
        'pinandbuy': pinandbuy,
        'prescriptionmedicine': prescriptionmedicine,
        'myFilter': myFilter,
    }
    return render(request, 'pharmacy/store.html', context)


def store(request, pharmacyid):
    customer = request.user.patient
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    name = request.user.first_name
    pharmacy = Pharmacist.objects.get(id=pharmacyid)
    groupname = str(request.user.groups.all()[0].name)
    items = order.cart_set.all()
    pinandbuy = False
    print(items)
    alert = False
    for item in items:
        if item.product.Pharmacist != pharmacy:
            order.delete()
            alert = True
            break

    products = specificproducts.objects.filter(Pharmacist=pharmacy)
    ordercount = order.get_cart_items
    myFilter = ProductFilter(request.GET, queryset=products)
    products = myFilter.qs
    if not request.user.is_authenticated:
        return redirect('loginUser')
    context = {
        'name': name,
        'products': products,
        'groupname': groupname,
        'ordercount': ordercount,
        'alert': alert,
        'pinandbuy': pinandbuy,
        'myFilter': myFilter,
    }
    return render(request, 'pharmacy/store.html', context)


def customercheckout(request):
    name = request.user.first_name
    customer = request.user.patient
    groupname = str(request.user.groups.all()[0].name)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    if order.shippingpossible == False:
        return redirect('cart')
    items = order.cart_set.all()
    ordercount = order.get_cart_items
    if not request.user.is_authenticated:
        return redirect('loginUser')
    context = {
        'name': name,
        'groupname': groupname,
        'items': items,
        'order': order,
        'customer': customer,
        'ordercount': ordercount,
    }
    return render(request, 'pharmacy/checkout.html', context)


def placeonlineorder(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    name = request.user.first_name
    customer = request.user.patient
    groupname = str(request.user.groups.all()[0].name)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    if order.shippingpossible == False:
        return redirect('cart')
    items = order.cart_set.all()
    ordercount = order.get_cart_items
    if ordercount < 1:
        return redirect('cart')
    for item in items:
        item.product.available = (item.product.available - item.quantity)
        item.product.save()
    order.complete = True
    order.save()
    return redirect('ordersuccess')


def placeofflineorder(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    name = request.user.first_name
    groupname = str(request.user.groups.all()[0].name)
    customer = request.user.pharmacist
    order, created = WalkinOrder.objects.get_or_create(
        customer=customer, complete=False)
    if order.shippingpossible == False:
        return redirect('walkincart')
    items = order.walkincart_set.all()
    ordercount = order.get_cart_items
    if ordercount < 1:
        return redirect('cart')
    for item in items:
        item.product.available = (item.product.available - item.quantity)
        item.product.save()
    order.complete = True
    order.save()
    return redirect('offlineorders')


def myorders(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    name = request.user.first_name
    groupname = str(request.user.groups.all()[0].name)
    customer = request.user.patient
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_cart_items
    orders = Order.objects.filter(complete=True, customer=customer)
    items = []
    button = False
    customerinfo = False
    for ord in orders:
        it = ord.cart_set.all()
        for item in it:
            items.append(item)
    context = {
        'name': name,
        'groupname': groupname,
        'items': items,
        'myorders': orders,
        'ordercount': ordercount,
    }
    return render(request, 'pharmacy/myorders.html', context)


def onlineorders(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    name = request.user.first_name
    groupname = str(request.user.groups.all()[0].name)
    customer = request.user.pharmacist
    order, created = WalkinOrder.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_cart_items
    pharmacy = request.user.pharmacist
    orders = Order.objects.filter(complete=True, delivered=False)
    button = True
    customerinfo = True
    items = []
    myorders = []
    for orderp in orders:
        itemst = orderp.cart_set.all()
        for item in itemst:
            if item.product.Pharmacist == pharmacy:
                myorders.append(orderp)
                break
    for order in myorders:
        itemlist = order.cart_set.all()
        for item in itemlist:
            items.append(item)

    context = {
        'name': name,
        'groupname': groupname,
        'ordercount': ordercount,
        'myorders': myorders,
        'items': items,
        'button': button,
        'customerinfo': customerinfo,
    }
    return render(request, 'pharmacy/orders.html', context)


def offlineorders(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    name = request.user.first_name
    groupname = str(request.user.groups.all()[0].name)
    customer = request.user.pharmacist
    order, created = WalkinOrder.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_cart_items
    pharmacy = request.user.pharmacist
    myorders = WalkinOrder.objects.filter(complete=True, customer=pharmacy)
    button = False
    customerinfo = False
    items = []
    for order in myorders:
        itemlist = order.walkincart_set.all()
        for item in itemlist:
            items.append(item)

    context = {
        'name': name,
        'groupname': groupname,
        'ordercount': ordercount,
        'myorders': myorders,
        'items': items,
        'button': button,
        'customerinfo': customerinfo,
    }
    return render(request, 'pharmacy/orders.html', context)


def sales(request):
    context = {}
    return render(request, '', context)


def ordersuccess(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    name = request.user.first_name
    customer = request.user.patient
    groupname = str(request.user.groups.all()[0].name)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_cart_items
    context = {
        'name': name,
        'groupname': groupname,
        'order': order,
        'customer': customer,
        'ordercount': ordercount,
    }
    return render(request, 'pharmacy/ordersuccess.html', context)


def updateitem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.patient
    product = specificproducts.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    cart, created = Cart.objects.get_or_create(order=order, product=product)

    if action == 'add':
        cart.quantity = (cart.quantity + 1)
    elif action == 'remove':
        cart.quantity = (cart.quantity - 1)

    cart.save()

    if cart.quantity <= 0:
        cart.delete()

    return JsonResponse('item was added', safe=False)


def updateitemwalkin(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.pharmacist
    product = specificproducts.objects.get(id=productId)
    order, created = WalkinOrder.objects.get_or_create(
        customer=customer, complete=False)
    cart, created = WalkinCart.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        cart.quantity = (cart.quantity + 1)
    elif action == 'remove':
        cart.quantity = (cart.quantity - 1)

    cart.save()

    if cart.quantity <= 0:
        cart.delete()

    return JsonResponse('item was added', safe=False)


def deliverorder(request):
    data = json.loads(request.body)
    orderID = data['orderId']
    order = Order.objects.get(id=orderID)
    order.delivered = True
    order.save()
    return JsonResponse('item delivered', safe=False)


def deleteproduct(request):
    data = json.loads(request.body)
    product = data['product']
    act = data['act']
    pharmacist = request.user.pharmacist
    product2 = specificproducts.objects.get(id=product)
    products = Cart.objects.filter(product=product2)
    walkincartproducts = WalkinCart.objects.filter(product=product2)
    if act == 'delete':
        for pro in products:
            pro.delete()
        for pro in walkincartproducts:
            pro.delete()
        product2.delete()

    elif act == 'inc':
        product2.available = (product2.available+1)
        product2.save()
    elif act == 'dec':
        product2.available = (product2.available-1)
        product2.save()

    if product2.available <= 0:
        for pro in products:
            pro.delete()
        for pro in walkincartproducts:
            pro.delete()
        product2.delete()

    return JsonResponse('item deleted ', safe=False)


def onlineorderscomplete(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    name = request.user.first_name
    groupname = str(request.user.groups.all()[0].name)
    customer = request.user.pharmacist
    order, created = WalkinOrder.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_cart_items
    pharmacy = request.user.pharmacist
    orders = Order.objects.filter(complete=True, delivered=True)
    button = False
    customerinfo = True
    items = []
    myorders = []
    for orderp in orders:
        itemst = orderp.cart_set.all()
        for item in itemst:
            if item.product.Pharmacist == pharmacy:
                myorders.append(orderp)
                break
    for order in myorders:
        itemlist = order.cart_set.all()
        for item in itemlist:
            items.append(item)

    context = {
        'name': name,
        'groupname': groupname,
        'ordercount': ordercount,
        'myorders': myorders,
        'items': items,
        'button': button,
        'customerinfo': customerinfo,
    }
    return render(request, 'pharmacy/orders.html', context)


# pharmacy material end
# -----------------------------------------------------------------------------

    # -------------------------------------------------------
    # new views


# ----------------------------------------------------------------------------
# pathologist material here

def testsadd(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')

    customer = request.user.pathologist
    order, created = AnonyTests.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_tests_items
    groupname = str(request.user.groups.all()[0].name)
    name = request.user.first_name
    pathology = request.user.pathologist
    pathoname = request.user.pathologist.PathoName
    pathologyid = request.user.pathologist.id

    form = addpro()
    if request.method == 'POST':
        form = addpro(request.POST, request.FILES)
        if form.is_valid():
            newform = form.save(commit=False)
            newform.Pathologist = pathology
            newform.save()
            return redirect('market')

    context = {
        'form': form,
        'name': name,
        'groupname': groupname,
        'ordercount': ordercount,
    }
    return render(request, 'pathology/testsadd.html', context)


def pathologistDashboard(request):
    customer = request.user.pathologist
    order, created = AnonyTests.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_tests_items
    groupname = str(request.user.groups.all()[0].name)
    name = request.user.first_name
    pathology = request.user.pathologist
    pathoname = request.user.pathologist.PathoName
    pathologyid = request.user.pathologist.id
    products = labtest.objects.filter(Pathologist=pathology)
    if not request.user.is_authenticated:
        return redirect('loginUser')
    context = {
        'name': name,
        'groupname': groupname,
        'products': products,
        'ordercount': ordercount,
    }
    return render(request, 'pathology/pathologistdashboard.html', context)


def alarmtests(request):
    customer = request.user.pathologist
    order, created = AnonyTests.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_tests_items
    groupname = str(request.user.groups.all()[0].name)
    name = request.user.first_name
    pathology = request.user.pathologist
    pathoname = request.user.pathologist.PathoName
    pathologyid = request.user.pathologist.id
    products = labtest.objects.filter(Pathologist=pathology)
    if not request.user.is_authenticated:
        return redirect('loginUser')
    context = {
        'name': name,
        'groupname': groupname,
        'products': products,
        'ordercount': ordercount,
    }
    return render(request, 'pathology/alarmtests.html', context)


def tests(request):
    name = request.user.first_name
    groupname = str(request.user.groups.all()[0].name)
    customer = request.user.patient
    order, created = BookTest.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_tests_items
    items = order.tests_set.all()
    if not request.user.is_authenticated:
        return redirect('loginUser')
    context = {
        'name': name,
        'groupname': groupname,
        'items': items,
        'order': order,
        'ordercount': ordercount,
    }
    return render(request, 'pathology/tests.html', context)


def market(request):
    name = request.user.first_name
    groupname = str(request.user.groups.all()[0].name)
    if not request.user.is_authenticated:
        return redirect('loginUser')
    customer = request.user.pathologist
    order, created = AnonyTests.objects.get_or_create(
        customer=customer, complete=False)
    items = order.addtests_set.all()
    ordercount = order.get_tests_items
    products = labtest.objects.filter(Pathologist=customer)
    context = {
        'name': name,
        'groupname': groupname,
        'items': items,
        'ordercount': ordercount,
        'products': products,
    }
    return render(request, 'pathology/market.html', context)


def addtests(request):
    name = request.user.first_name
    groupname = str(request.user.groups.all()[0].name)
    customer = request.user.pathologist
    order, created = AnonyTests.objects.get_or_create(
        customer=customer, complete=False)
    items = order.addtests_set.all()
    ordercount = order.get_tests_items
    if not request.user.is_authenticated:
        return redirect('loginUser')
    context = {
        'name': name,
        'groupname': groupname,
        'items': items,
        'order': order,
        'ordercount': ordercount,
    }
    return render(request, 'pathology/addtests.html', context)


def pathology(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    customer = request.user.patient
    order, created = BookTest.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_tests_items
    groupname = str(request.user.groups.all()[0].name)
    name = request.user.first_name
    labs = Pathologist.objects.all()

    r = requests.get('https://get.geojs.io/')
    ip_request = requests.get('https://get.geojs.io/v1/ip.json')
    ipAdd = ip_request.json()['ip']
    url = 'https://get.geojs.io/v1/ip/geo/'+ipAdd+'.json'
    geo_request = requests.get(url)
    geo_data = geo_request.json()
    print(geo_data['city'])
    mycity = geo_data['city']
    print(mycity)
    labs = labs.filter(PathoAddress=mycity)

    context = {
        'name': name,
        'groupname': groupname,
        'labs': labs,
        'ordercount': ordercount,
    }
    return render(request, 'pathology/pathology.html', context)


def dukan(request, pathologyid):
    customer = request.user.patient
    order, created = BookTest.objects.get_or_create(
        customer=customer, complete=False)
    name = request.user.first_name
    pathology = Pathologist.objects.get(id=pathologyid)
    groupname = str(request.user.groups.all()[0].name)
    items = order.tests_set.all()
    print(items)
    alert = False
    for item in items:
        if item.product.Pathologist != pathology:
            order.delete()
            alert = True
            break

    products = labtest.objects.filter(Pathologist=pathology)
    ordercount = order.get_tests_items
    if not request.user.is_authenticated:
        return redirect('loginUser')
    context = {
        'name': name,
        'products': products,
        'groupname': groupname,
        'ordercount': ordercount,
        'alert': alert,
    }
    return render(request, 'pathology/dukan.html', context)


def outcheck(request):
    name = request.user.first_name
    customer = request.user.patient
    groupname = str(request.user.groups.all()[0].name)
    order, created = BookTest.objects.get_or_create(
        customer=customer, complete=False)

    items = order.tests_set.all()
    ordercount = order.get_tests_items
    if not request.user.is_authenticated:
        return redirect('loginUser')
    context = {
        'name': name,
        'groupname': groupname,
        'items': items,
        'order': order,
        'customer': customer,
        'ordercount': ordercount,
    }
    return render(request, 'pathology/outcheck.html', context)


def flipkart(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    name = request.user.first_name
    customer = request.user.patient
    groupname = str(request.user.groups.all()[0].name)
    order, created = BookTest.objects.get_or_create(
        customer=customer, complete=False)

    items = order.tests_set.all()
    ordercount = order.get_tests_items
    if ordercount < 0:
        return redirect('tests')
    for item in items:
        item.product.available = (item.product.available - item.quantity)

        item.product.save()
    order.complete = True
    order.save()
    return redirect('successorder')


def amazon(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    name = request.user.first_name
    groupname = str(request.user.groups.all()[0].name)
    customer = request.user.pathologist
    order, created = AnonyTests.objects.get_or_create(
        customer=customer, complete=False)

    items = order.addtests_set.all()
    ordercount = order.get_tests_items
    if ordercount < 1:
        return redirect('tests')
    for item in items:
        item.product.available = (item.product.available - item.quantity)
        item.product.save()
    order.complete = True
    order.save()
    return redirect('orderoffline')


def itsmychoice(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    name = request.user.first_name
    groupname = str(request.user.groups.all()[0].name)
    customer = request.user.patient
    order, created = BookTest.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_tests_items
    orders = BookTest.objects.filter(complete=True, customer=customer)
    items = []
    button = False
    customerinfo = False
    for ord in orders:
        it = ord.tests_set.all()
        for item in it:
            items.append(item)
    context = {
        'name': name,
        'groupname': groupname,
        'items': items,
        'myorders': orders,
        'ordercount': ordercount,
    }
    return render(request, 'pathology/itsmychoice.html', context)


def orderonline(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    name = request.user.first_name
    groupname = str(request.user.groups.all()[0].name)
    customer = request.user.pathologist
    order, created = AnonyTests.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_tests_items
    pathology = request.user.pathologist
    orders = BookTest.objects.filter(complete=True, delivered=False)
    button = True
    customerinfo = True
    items = []
    myorders = []
    for orderp in orders:
        itemst = orderp.tests_set.all()
        for item in itemst:
            if item.product.Pathologist == pathology:
                myorders.append(orderp)
                break
    for order in myorders:
        itemlist = order.tests_set.all()
        for item in itemlist:
            items.append(item)

    context = {
        'name': name,
        'groupname': groupname,
        'ordercount': ordercount,
        'myorders': myorders,
        'items': items,
        'button': button,
        'customerinfo': customerinfo,
    }
    return render(request, 'pathology/orderonline.html', context)


def orderoffline(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    name = request.user.first_name
    groupname = str(request.user.groups.all()[0].name)
    customer = request.user.pathologist
    order, created = AnonyTests.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_tests_items
    pathology = request.user.pathologist
    myorders = AnonyTests.objects.filter(complete=True, customer=pathology)
    button = False
    customerinfo = False
    items = []
    for order in myorders:
        itemlist = order.addtests_set.all()
        for item in itemlist:
            items.append(item)

    context = {
        'name': name,
        'groupname': groupname,
        'ordercount': ordercount,
        'myorders': myorders,
        'items': items,
        'button': button,
        'customerinfo': customerinfo,
    }
    return render(request, 'pathology/orderonline.html', context)


def bikari(request):
    context = {}
    return render(request, '', context)


def successorder(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    name = request.user.first_name
    customer = request.user.patient
    groupname = str(request.user.groups.all()[0].name)
    order, created = BookTest.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_tests_items
    context = {
        'name': name,
        'groupname': groupname,
        'order': order,
        'customer': customer,
        'ordercount': ordercount,
    }
    return render(request, 'pathology/successorder.html', context)


def itemupdating(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.patient
    product = labtest.objects.get(id=productId)
    order, created = BookTest.objects.get_or_create(
        customer=customer, complete=False)
    cart, created = Tests.objects.get_or_create(order=order, product=product)

    if action == 'add':
        cart.quantity = 1
    elif action == 'remove':
        cart.quantity = 0

    cart.save()

    if cart.quantity <= 0:
        cart.delete()

    return JsonResponse('item was added', safe=False)


def itemupdatedwalkin(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.pathologist
    product = labtest.objects.get(id=productId)
    order, created = AnonyTests.objects.get_or_create(
        customer=customer, complete=False)
    cart, created = AddTests.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        cart.quantity = 1
    elif action == 'remove':
        cart.quantity = 0

    cart.save()

    if cart.quantity <= 0:
        cart.delete()

    return JsonResponse('item was added', safe=False)


def ekart(request):
    data = json.loads(request.body)
    orderID = data['orderId']
    order = BookTest.objects.get(id=orderID)
    order.delivered = True
    order.save()
    return JsonResponse('item delivered', safe=False)


def removeproduct(request):
    data = json.loads(request.body)
    product = data['product']
    act = data['act']
    pathologist = request.user.pathologist
    product2 = labtest.objects.get(id=product)
    products = Tests.objects.filter(product=product2)
    walkincartproducts = AddTests.objects.filter(product=product2)
    if act == 'delete':
        for pro in products:
            pro.delete()
        for pro in walkincartproducts:
            pro.delete()
        product2.delete()

    elif act == 'inc':
        product2.available = product2.available
        product2.save()
    elif act == 'dec':
        product2.available = product2.available
        product2.save()

    if product2.available <= 0:
        for pro in products:
            pro.delete()
        for pro in walkincartproducts:
            pro.delete()
        product2.delete()

    return JsonResponse('item deleted ', safe=False)


def completedorder(request):
    if not request.user.is_authenticated:
        return redirect('loginUser')
    name = request.user.first_name
    groupname = str(request.user.groups.all()[0].name)
    customer = request.user.pathologist
    order, created = AnonyTests.objects.get_or_create(
        customer=customer, complete=False)
    ordercount = order.get_tests_items
    pathology = request.user.pathologist
    orders = BookTest.objects.filter(complete=True, delivered=True)
    button = False
    customerinfo = True
    items = []
    myorders = []
    for orderp in orders:
        itemst = orderp.tests_set.all()
        for item in itemst:
            if item.product.Pathologist == pathology:
                myorders.append(orderp)
                break
    for order in myorders:
        itemlist = order.tests_set.all()
        for item in itemlist:
            items.append(item)

    context = {
        'name': name,
        'groupname': groupname,
        'ordercount': ordercount,
        'myorders': myorders,
        'items': items,
        'button': button,
        'customerinfo': customerinfo,
    }
    return render(request, 'pathology/orderonline.html', context)

# pathologist material end
# -----------------------------------------------------------------------------


def videocall(request, meetingid):
    if not request.user.is_authenticated:
        return redirect('loginUser')

    return render(request, 'index.html', {
        'agora_id': '211afdfa7ce3483ab760444a2b23ec91', 'channel': meetingid, 'channel_end_url': '/', 'title': 'upcare'})
