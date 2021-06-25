from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing, Bid, Comment, Watchlist

# Create new form based on Listing model (from Django docs)
class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image', 'category']

class NewBidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_amount']

class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

def index(request):
    listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "listings": listings
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
        # Create initial bid for listing, equal to starting price
        bid = Bid(listing=new_listing, bidder=request.user, bid_amount=new_listing.starting_bid)
        bid.save()
        return HttpResponseRedirect(reverse("index"))

    # Below code runs when method is "GET"
    return render(request, "auctions/new_listing.html", {
        "form": NewListingForm()
    })


def listing(request, listing_id):
    listing = Listing.objects.get(pk=int(listing_id))
    top_bid = listing.get_highest_bid()
    form = NewCommentForm()
    return render(request, "auctions/listing.html", {
        "listing": listing, "top_bid": top_bid, "form": form
    })


def bid(request):
    print(request)
    if request.method == "POST":
        bid = NewBidForm(request.POST)
        new_bid = bid.save(commit=False)
        new_bid.bidder = request.user
        new_bid.listing = Listing.objects.get(pk=int(request.POST["listing"]))
        new_bid.save()
        return HttpResponseRedirect(reverse("index"))

    # Below code runs when method is "GET"
    listing = Listing.objects.get(pk=int(request.GET["listing"]))
    top_bid = listing.get_highest_bid()
    return render(request, "auctions/bid.html", {
        "listing": listing, "top_bid": top_bid, "form": NewBidForm()
    })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Listing.objects.values_list('category').distinct()
    })


def category(request, category):
    listings = Listing.objects.filter(category=category).filter(active=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def comment(request):
    comment = NewCommentForm(request.POST)
    print(comment)
    new_comment = comment.save(commit=False)
    new_comment.user = request.user
    new_comment.listing = Listing.objects.get(pk=int(request.POST["listing"]))
    new_comment.save()
    return HttpResponseRedirect(reverse("listing", args=(new_comment.listing.id,)))