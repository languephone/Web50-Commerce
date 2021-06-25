from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("bid", views.bid, name="bid"),
    path("categories", views.categories, name="categories"),
    path("comment", views.comment, name="comment"),
    path("<int:listing_id>", views.listing, name="listing"),
    path("<str:category>", views.category, name="category"),
]
