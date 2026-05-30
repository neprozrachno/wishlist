from django.contrib import admin
from .models import Wishlist, Gift, Notification, Favorite


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display  = ['title', 'owner', 'event_type', 'privacy', 'status', 'created_at']
    list_filter   = ['privacy', 'status', 'event_type']
    search_fields = ['title', 'owner__username']


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display  = ['name', 'wishlist', 'category', 'price', 'priority', 'status']
    list_filter   = ['category', 'priority', 'status']
    search_fields = ['name', 'wishlist__title']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['recipient', 'message', 'is_read', 'created_at']
    list_filter   = ['is_read']
    search_fields = ['recipient__username', 'message']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display  = ['user', 'gift', 'created_at']
    search_fields = ['user__username', 'gift__name']