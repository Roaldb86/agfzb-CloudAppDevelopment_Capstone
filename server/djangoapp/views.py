from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import requests
import json
from . import models
from . import restapis

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/user_login_bootstrap.html', context)
    else:
        return render(request, 'djangoapp/user_login_bootstrap.html', context)


# Create a `logout_request` view to handle sign out request

def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

def get_dealerships(request):
    if request.method == "GET":
        url = 'https://eu-gb.functions.appdomain.cloud/api/v1/web/roaldb_dev/djangoapp/dealership'
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        context = {"dealerships": get_dealers_from_cf(url)}
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = 'https://eu-gb.functions.appdomain.cloud/api/v1/web/roaldb_dev/djangoapp/review-get'
        # Get dealers from the URL
           # Concat all dealer's short name
        context = {"reviews": get_dealer_reviews_from_cf(url, dealerId=dealer_id)}
        # Return a list of dealer short name
        return render(request, 'djangoapp/dealer_details.html', context)


def add_review(request, dealer_id):
    if request.method == "GET":
        url = f'https://eu-gb.functions.appdomain.cloud/api/v1/web/roaldb_dev/djangoapp/dealership?dealerId={dealer_id}'
        # Get dealers from the URL
        context = {
            "dealer_id": dealer_id,
            "cars": models.CarModel.objects.all(),
            "dealers": restapis.get_dealers_from_cf(url),
        }

        return render(request, 'djangoapp/add_review.html', context)

    elif request.method == "POST":
        if request.user.is_authenticated:
            form = request.POST
            print("form print", form)
            review = {
                "time": datetime.utcnow().isoformat(),
                "name": f"{request.user.first_name} {request.user.last_name}",
                "dealership": dealer_id,
                "review": form["content"],
                }

            json_payload = {"review": review}
            print(json_payload)
            url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/roaldb_dev/djangoapp/review-post"
            post_request(url, json_payload, dealerId=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)


