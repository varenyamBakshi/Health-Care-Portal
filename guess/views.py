from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from .forms import *
from .models import *
from django.conf import settings
from django.http import JsonResponse
from django.views.generic import ListView
import os
import json
import joblib
import pandas as pd
import numpy as np

# Create your views here.
def index(request):
    cls = joblib.load('decision_tree.joblib') # classification model
    cls1 = joblib.load('gradient_boost.joblib')
   
    cls3 = joblib.load('random_forest.joblib')
    symp_list = pd.read_csv('test_data.csv').columns[:-1]
    d = np.zeros((len(symp_list)))
    test_case = pd.DataFrame(d).transpose()
    test_case.columns= symp_list
    output = False
    form = guessform()
    context = {
        'form':form,
        'output':output,
    }
    if request.method == 'POST':
        form = guessform(request.POST)
        if form.is_valid():
            symptoms = form.cleaned_data['symptoms']   # need to input exact coulmn names with comma separated value
            symptoms = symptoms.split(',')
            for symp in symptoms:
                if symp in symp_list: test_case.loc[0, [symp]]=1   
            disease = cls.predict(test_case)   #predicted disease 
            disease1 = cls1.predict(test_case)
           
            disease3 = cls3.predict(test_case)
            output = True
            print(disease)
            context = {
                'disease1':disease[0],
                'disease3':disease3[0],
                'disease4':disease1[0],
                'form':form,
                'output':output,
            }
            
    return render(request, 'main.html', context)

