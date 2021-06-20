from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listings(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=1000)
    starting_bid = models.DecimalField(decimal_places=2, max_digits=9)
    image = models.URLField(blank=True)
    category = models.CharField(max_length=64)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller_listings")
    creation_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}: £{self.starting_bid} (Active:{self.active})"


class Bids(models.Model):
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bid_history")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder_bids")
    bid_amount = models.DecimalField(decimal_places=2, max_digits=9)
    date_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"listing {self.listing}: £{self.bid_amount}"


class Comments(models.Model):
    pass


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users_watching")
    listing = models.ManyToManyField(Listings, blank=True, related_name="on_watchlists")
    date_added = models.DateTimeField(auto_now_add=True)
