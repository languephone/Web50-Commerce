from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
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

@login_required(login_url='/login')
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
    bid_form = NewBidForm()
    comment_form = NewCommentForm()
    return render(request, "auctions/listing.html", {
        "listing": listing, "top_bid": top_bid, "bid_form": bid_form,
        "comment_form": comment_form
    })

@login_required(login_url='/login')
def bid(request, listing_id):
    if request.method == "GET":
        return HttpResponse("Error: Please bid via the form.")
    # Create bid object but don't commit, then check if it's higher than the existing high bid.
    bid = NewBidForm(request.POST)
    new_bid = bid.save(commit=False)
    new_bid.bidder = request.user
    new_bid.listing = Listing.objects.get(pk=int(listing_id))
    current_high_bid = new_bid.listing.get_highest_bid()['bid_amount__max']
    if new_bid.bid_amount <= current_high_bid:
        return HttpResponse("Error: Your bid must be higher than the existing bid.")
    else:
        new_bid.save()
        return HttpResponseRedirect(reverse("index"))


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Listing.objects.values_list('category').distinct()
    })


def category(request, category):
    listings = Listing.objects.filter(category=category).filter(active=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def comment(request, listing_id):
    comment = NewCommentForm(request.POST)
    new_comment = comment.save(commit=False)
    new_comment.user = request.user
    new_comment.listing = Listing.objects.get(pk=int(listing_id))
    new_comment.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required(login_url='/login')
def watchlist(request, listing_id):
    if request.method == "POST":
        # Create new watchlist for user if one doesn't already exist:
        user = request.user
        listing = Listing.objects.get(pk=int(listing_id))
        if Watchlist.objects.filter(user=int(user.id)).exists():
            watchlist = Watchlist.objects.get(user=int(user.id))
            watchlist.listing.add(listing_id)
        else:
            watchlist = Watchlist(user=user)
            watchlist.save()
            watchlist.listing.add(listing_id)        
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

    # TODO: create view for get method showing items in watchlist.
