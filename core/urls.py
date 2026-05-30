from django.urls import path
from . import views

urlpatterns = [
    # Авторизация
    path('',        views.login_view,  name='home'),   # главная → страница входа
    path('login/',  views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Профиль
    path('profile/',              views.profile_view,        name='profile'),
    path('u/<str:username>/',     views.public_profile_view, name='public_profile'),
    path('feed/',                 views.public_feed_view,    name='public_feed'),

    # Вишлисты
    path('wishlists/create/',                    views.wishlist_create_view,   name='wishlist_create'),
    path('wishlists/<int:pk>/',                  views.wishlist_detail_view,   name='wishlist_detail'),
    path('wishlists/<int:pk>/edit/',             views.wishlist_edit_view,     name='wishlist_edit'),
    path('wishlists/<int:pk>/delete/',           views.wishlist_delete_view,   name='wishlist_delete'),
    path('wishlists/share/<str:token>/',         views.wishlist_by_token_view, name='wishlist_by_token'),

    # Подарки
    path('wishlists/<int:wishlist_pk>/gifts/add/', views.gift_create_view,          name='gift_create'),
    path('gifts/<int:pk>/edit/',                   views.gift_edit_view,            name='gift_edit'),
    path('gifts/<int:pk>/delete/',                 views.gift_delete_view,          name='gift_delete'),
    path('gifts/<int:pk>/reserve/',                views.gift_reserve_view,         name='gift_reserve'),
    path('gifts/<int:pk>/unreserve/',              views.gift_unreserve_view,       name='gift_unreserve'),
    path('gifts/<int:pk>/favorite/',               views.gift_favorite_toggle_view, name='gift_favorite_toggle'),

    # Личный кабинет
    path('reservations/',  views.my_reservations_view, name='my_reservations'),
    path('notifications/', views.notifications_view,   name='notifications'),
    path('favorites/',     views.favorites_view,        name='favorites'),
]