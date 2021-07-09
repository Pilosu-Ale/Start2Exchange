from django.shortcuts import render, HttpResponseRedirect
from .forms import FormRegistration
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from app.models import Profile
from random import *


def registration(request):
    if request.method == 'POST':
        form = FormRegistration(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]
            user = User.objects.create_user(username=username, password=password, email=email)
            BTC_wallet = randint(1, 10)
            Profile.objects.create(user=user, BTC_wallet=BTC_wallet)
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect("/")
    else:
        form = FormRegistration()
    context = {"form": form}
    return render(request, "accounts/registration.html", context)