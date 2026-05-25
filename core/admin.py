from django.contrib import admin
from .models import Wishlist, Gift

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'event_type', 'privacy', 'status', 'created_at']
    list_filter  = ['privacy', 'status', 'event_type']
    search_fields = ['title', 'owner__username']

@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ['name', 'wishlist', 'category', 'price', 'priority', 'status']
    list_filter  = ['category', 'priority', 'status']
    search_fields = ['name', 'wishlist__title']
