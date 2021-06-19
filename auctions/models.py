from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listings(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=1000)
    starting_bid = models.DecimalField(decimal_places=2, max_digits=9)
    image = models.URLField()
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.title}: £{self.starting_bid}"


class Bids(models.Model):
    pass


class Comments(models.Model):
    pass