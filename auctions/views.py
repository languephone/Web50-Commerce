from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listings, Bids, Comments, Watchlist

# Create new form based on Listings model (from Django docs)
class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listings
        fields = ['title', 'description', 'starting_bid', 'image', 'category']

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listings.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def new_listing(request):
    if request.method == "POST":
        # Use Django's ModelForm class to process form
        # Create instance of model, but don't commit until seller foreign key added 
        listing = NewListingForm(request.POST)
        new_listing = listing.save(commit=False)
        new_listing.seller = request.user
        new_listing.save()
        return HttpResponseRedirect(reverse("index"))

    # Below code runs when method is "GET"
    return render(request, "auctions/new_listing.html", {
        "form": NewListingForm()
    })


def listing(request, listing_id):
    listing = Listings.objects.get(pk=int(listing_id))
    bids = Bids.objects.all().order_by('date_time')
    return render(request, "auctions/listing.html", {
        "listing":listing, "bids":bids
    })
