from django.contrib import admin

from .models import User, Listings, Bids, Comments, Watchlist

# Register your models here.
class UserAdmin(admin.ModelAdmin):
	list_display = ("username", "email", "id")

admin.site.register(User, UserAdmin)
admin.site.register(Listings)
admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(Watchlist)