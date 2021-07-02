from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    
    def get_watchlist(self):
        """Return a user's watchlist, if it exists."""
        
        # Check if watchlist exists
        if Watchlist.objects.filter(user=self).exists():
            watchlist = Watchlist.objects.get(user=self)
            listings = watchlist.listing.all()
            return listings
        else:
            return None


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=1000)
    starting_bid = models.DecimalField(decimal_places=2, max_digits=9)
    image = models.URLField(blank=True)
    category = models.CharField(max_length=64)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller_listings")
    creation_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)

    def get_highest_bid(self):
        """Return current highest bid for listing by referencing Bid table."""
        
        if self.bid_history.exists():
            top_bid = self.bid_history.all().aggregate(
                models.Max('bid_amount'))['bid_amount__max']
        else:
            top_bid = self.starting_bid
        return top_bid

    def get_highest_bidder(self):
        """Return bid object for highest bid by referencing Bid table."""

        """Queries the most recent bid, relying on logic in the bidding route
        which only allows bids greater than the existing top bid."""
        high_bid = self.bid_history.all().order_by('bid_amount').reverse()[0]
        high_bidder = high_bid.bidder
        return high_bidder

    def get_bid_count(self):
        """Return number of bids on current listing."""

        if self.bid_history.exists():
            bids = len(self.bid_history.all())
        else:
            bids = 0
        return bids

    def toggle_watchlist(self, user):
        """Add an item to a watchlist, or remove it if it's already there."""
        
        # Check if watchlist exists, then add/remove
        if Watchlist.objects.filter(user=user).exists():
            watchlist = Watchlist.objects.get(user=user)
            if self in watchlist.listing.all():
                watchlist.listing.remove(self)
            else:
                watchlist.listing.add(self)
        # If watchlist doesn't exist, create new watchlist then add listing
        else:
            watchlist = Watchlist(user=user)
            watchlist.save()
            watchlist.listing.add(self)       
    
    def __str__(self):
        return f"{self.title}: £{self.starting_bid} (Active:{self.active})"


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid_history")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder_bids")
    bid_amount = models.DecimalField(decimal_places=2, max_digits=9)
    date_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bid: {self.listing.title} £{self.bid_amount}"


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE,related_name="listing_comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    comment = models.TextField(max_length=1000)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment: {self.listing.title}: {self.comment[:15]}..."


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_watchlist")
    listing = models.ManyToManyField(Listing, blank=True, related_name="on_watchlists")
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s watchlist"
