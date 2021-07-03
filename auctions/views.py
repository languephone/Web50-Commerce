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
        return HttpResponseRedirect(reverse("index"))

    # Below code runs when method is "GET"
    return render(request, "auctions/new_listing.html", {
        "form": NewListingForm()
    })


def listing(request, listing_id):
    listing = Listing.objects.get(pk=int(listing_id))
    top_bid = listing.get_highest_bid()
    # Check if listing in user's watchlist to toggle badge & removal button
    try:
        watchlist = request.user.get_watchlist()
    except AttributeError:
        watchlist = False
    # Need to check watchlist exists, otherwise will give error
    if watchlist and listing in watchlist:
        watchlist = True
    else:
        watchlist = False
    bid_form = NewBidForm()
    comment_form = NewCommentForm()
    return render(request, "auctions/listing.html", {
        "listing": listing, "top_bid": top_bid, "watchlist": watchlist,
        "bid_form": bid_form, "comment_form": comment_form
    })


@login_required(login_url='/login')
def bid(request, listing_id):
    if request.method == "GET":
        return HttpResponse("Error: Please bid via the form.")
    
    # Create bid object from form data, but don't commit
    bid = NewBidForm(request.POST)
    new_bid = bid.save(commit=False)
    new_bid.bidder = request.user
    new_bid.listing = Listing.objects.get(pk=int(listing_id))
    current_price = new_bid.listing.get_highest_bid()
    
    # Prevent seller from bidding
    if new_bid.bidder == new_bid.listing.seller:
        return HttpResponse("Error: You can't bid on your own listing")
    # Prevent bidding on a closed auction
    if new_bid.listing.active == False:
        return HttpResponse("This auction is already closed")
    
    # If bids already exist, new bid must be > existing bids
    if new_bid.listing.bid_history.exists():
        if new_bid.bid_amount <= current_price:
            return HttpResponse("Error: Your bid must be higher than the existing bid.")
    # Where no bids exist, new bid must only be >= starting price
    else:
        if new_bid.bid_amount < current_price:
            return HttpResponse("Error: Your bid must at least match the starting price.")
    
    # Save new bid if neither conditional met
    new_bid.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Listing.objects.values_list('category').distinct()
    })


def category(request, category):
    listings = Listing.objects.filter(category=category).filter(active=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


@login_required(login_url='/login')
def comment(request, listing_id):
    comment = NewCommentForm(request.POST)
    new_comment = comment.save(commit=False)
    new_comment.user = request.user
    new_comment.listing = Listing.objects.get(pk=int(listing_id))
    new_comment.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


@login_required(login_url='/login')
def watchlist(request):
    user = request.user
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        # Create new watchlist for user if one doesn't already exist:
        listing = Listing.objects.get(pk=int(listing_id))
        listing.toggle_watchlist(user) 
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

    # Below code runs when method is "GET"
    listings = user.get_watchlist()
    return render(request, "auctions/index.html", {
        "listings": listings
    })


@login_required(login_url='/login')
def close_auction(request, listing_id):
    # Check if request coming from user who listed the item
    user = request.user
    listing = Listing.objects.get(pk=int(listing_id))
    print(f"user: {user}, listing: {listing.seller}")
    if user != listing.seller:
        return HttpResponse("You must be the seller to close an auction.")  
    
    if request.method == "POST":
        high_bidder = listing.get_highest_bidder()
        listing.active = False
        listing.winner = high_bidder
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

    # Below code runs when method is "GET"
    return HttpResponse("This page is not accessible.")


@login_required(login_url='/login')
def my_listings(request):
    user = request.user
    listings = user.seller_listings.all()
    return render(request, "auctions/index.html", {
        "listings": listings
    })