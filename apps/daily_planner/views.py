# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from . models import *
import time
from datetime import datetime
from datetime import date
from datetime import timedelta

import re
EMAIL_REGEX = re.compile (r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


# Create your views here.
def index(request):
    context = {}
    if 'invalid_login' in request.session:
        request.session.pop('invalid_login')
        context['login_messages'] = True
    elif 'invalid_registration' in request.session:
        request.session.pop('invalid_registration')
        context['registration_messages'] = True

    return render(request, 'daily_planner/index.html', context)

def register(request):
    if request.method == 'POST':
        isValid=True
        if len(request.POST['first_name']) < 1:
            messages.add_message(request, messages.ERROR, "Please enter your first name.")
            isValid = False
        elif not request.POST['first_name'].isalpha():
            messages.add_message(request, messages.ERROR,"Please enter a valid first name.")
            isValid = False

        if len(request.POST['last_name']) < 1:
            messages.add_message(request, messages.ERROR, "Please enter your last name.")
            isValid = False
        elif not request.POST['last_name'].isalpha():
            messages.add_message(request, messages.ERROR,"Please enter a valid last name.")
            isValid = False

        if len(request.POST['email']) < 1:
            messages.add_message(request, messages.ERROR, "Please enter a valid email.")
            isValid = False
        elif not EMAIL_REGEX.match(request.POST['email']):
            messages.add_message(request, messages.ERROR, "Invalid Email. Please Re-Enter! ")
            isValid = False

        if len(request.POST['password']) < 9:
            messages.add_message(request, messages.ERROR, "Password must be longer than 8 characters.")
            isValid = False
        elif request.POST['password'] != request.POST['confirm_password']:
            messages.add_message(request, messages.ERROR, "Password and Confirm do not match!")
            isValid = False

        if not isValid:
            request.session['invalid_registration'] = True
            return redirect('/')
        else:
            new_user = User.objects.create(first_name=request.POST['first_name'],aka=request.POST['aka'], last_name=request.POST['last_name'], email=request.POST['email'], password=request.POST['password'], birthdate=request.POST['birthdate'])
            request.session['first_name']=new_user.first_name
            request.session['email']=new_user.email
            return redirect('daily_planner:home')

def login(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST['email'])
            request.session['email'] = request.POST['email']

            if user.password==request.POST['password']:
                request.session['first_name'] = user.first_name
                return redirect ('daily_planner:home')
            else:
                request.session['invalid_login'] = True
                messages.add_message(request, messages.ERROR,"Password is invalid.")
                return redirect('daily_planner:login')
        except:
            request.session['invalid_login'] = True
            messages.add_message(request, messages.ERROR,"That email is not registered!")
            return redirect('daily_planner:login')

def homepage(request):
    today = date.today()
    tomorrow= today + timedelta(1)
    # appointments = Appointment.objects.all()
    todayappt = Appointment.objects.filter(date = today)
    futureappt=Appointment.objects.filter(date__gt= tomorrow)
    context={
        'first_name':request.session['first_name'],
        'appointments': Appointment.objects.all(),
        'today':today,
        'todayappt': todayappt,
        'futureappt':futureappt
        }
    print context['appointments']

    return render(request, 'daily_planner/homepage.html', context)



def add_appointment(request):
    if request.method == "POST":
        today = datetime.now()
        errors = "false"

        if len(request.POST['task']) < 1:
            messages.error(request, "please enter a name for your appointment in task")
            errors = "true"
        if str(today) > date:
            print "You entered an invalid date/time, please re-enter."
            messages.error(request, 'Please enter a valid appointment date/time')
            errors = "true"
        if len(request.POST['time']) < 5:
            messages.error(request, 'please enter a valid time for your appointment')
            errors = "true"

        if errors == "true":
            return redirect('/homepage')
        else:
            print "that is a valid date and time you entered!"
            Appointment.objects.create(task=request.POST['task'], date=request.POST['date'],status="Pending", time=request.POST['time'], user_id = User.objects.get(first_name=request.session['first_name']).id)

    return redirect('daily_planner:homepage')



def edit_appointment(request, id):
    appointment={}
    context = {
        "appointment": Appointment.objects.get(id=id)
        }

    return render(request, 'daily_planner/edit_appointment.html', context)

def update_appointment(request):
    if request.method=='POST':
        appointment=Appointment.objects.get(id=request.POST['update'])
        appointment.task=request.POST['task']
        appointment.date=request.POST['date']
        appointment.time=request.POST['time']
        appointment.save()
    return redirect('daily_planner:homepage')

def delete_appointment(request, id):
    Appointment.objects.filter(id=id).delete()
    return redirect('daily_planner:homepage')

def logout(request):
    request.session.clear()
    return redirect('/')
