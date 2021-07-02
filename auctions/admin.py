from django.contrib import admin

from .models import User, Listing, Bid, Comment, Watchlist

# Register your models here.
class UserAdmin(admin.ModelAdmin):
	list_display = ("username", "email", "id")

class BidAdmin(admin.ModelAdmin):
	list_display = ("listing", "bid_amount", "bidder")

admin.site.register(User, UserAdmin)
admin.site.register(Listing)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment)
admin.site.register(Watchlist)