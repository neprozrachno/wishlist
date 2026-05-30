from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404
from .models import Wishlist, Gift, Favorite
from .forms import LoginForm, RegisterForm, WishlistForm, GiftForm
from .facade import WishlistFacade
from .observer import event_manager
from .strategy import get_template_strategy


# ===== АВТОРИЗАЦИЯ =====

def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    error = ''
    register_form = RegisterForm()
    mode = request.POST.get('mode', 'login')

    if request.method == 'POST':
        if mode == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                error = 'Неверный логин или пароль.'

        elif mode == 'register':
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                return redirect('profile')
            else:
                errors = []
                for field, errs in register_form.errors.items():
                    for e in errs:
                        errors.append(e)
                error = ' '.join(errors)

        elif mode == 'guest':
            return redirect('public_feed')

    return render(request, 'core/login.html', {
        'error': error,
        'mode': mode,
        'register_form': register_form,
    })


def logout_view(request):
    logout(request)
    return redirect('login')


# ===== ПРОФИЛЬ =====

@login_required
def profile_view(request):
    wishlists = WishlistFacade.get_user_wishlists(request.user)
    return render(request, 'core/profile.html', {'wishlists': wishlists})


def public_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    wishlists = user.wishlists.filter(privacy='public', status='active')
    return render(request, 'core/public_profile.html', {
        'profile_user': user,
        'wishlists': wishlists,
    })


def public_feed_view(request):
    """Лента публичных вишлистов — стратегия выбирает шаблон для гостя или авторизованного"""
    wishlists = WishlistFacade.get_public_wishlists()
    strategy = get_template_strategy(request.user)
    return render(request, strategy.get_feed_template(), {'wishlists': wishlists})


# ===== ВИШЛИСТЫ =====

@login_required
def wishlist_create_view(request):
    form = WishlistForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        wl = WishlistFacade.create_wishlist(
            owner=request.user,
            title=form.cleaned_data['title'],
            event_type=form.cleaned_data['event_type'],
            event_date=form.cleaned_data.get('event_date'),
            privacy=form.cleaned_data['privacy'],
            comment=form.cleaned_data.get('comment', ''),
        )
        messages.success(request, f'Вишлист «{wl.title}» создан!')
        return redirect('wishlist_detail', pk=wl.pk)
    return render(request, 'core/wishlist_form.html', {'form': form, 'action': 'create'})


@login_required
def wishlist_edit_view(request, pk):
    wl = get_object_or_404(Wishlist, pk=pk, owner=request.user)
    form = WishlistForm(request.POST or None, instance=wl)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Вишлист обновлён!')
        return redirect('wishlist_detail', pk=wl.pk)
    return render(request, 'core/wishlist_form.html', {'form': form, 'action': 'edit', 'wishlist': wl})


@login_required
def wishlist_delete_view(request, pk):
    wl = get_object_or_404(Wishlist, pk=pk, owner=request.user)
    if request.method == 'POST':
        title = wl.title
        reserved_gifts = wl.gifts.filter(status='reserved')
        for gift in reserved_gifts:
            if gift.reserved_by:
                event_manager.notify('wishlist_deleted', {
                    'gift_name': gift.name,
                    'wl_title': title,
                    'reserver': gift.reserved_by,
                })
        wl.delete()
        messages.success(request, f'Вишлист «{title}» удалён.')
        return redirect('profile')
    return render(request, 'core/wishlist_confirm_delete.html', {'wishlist': wl})


def wishlist_detail_view(request, pk):
    """Детальная страница вишлиста — стратегия выбирает шаблон для гостя или авторизованного"""
    wl = get_object_or_404(Wishlist, pk=pk)
    if wl.privacy == 'private' and wl.owner != request.user:
        raise Http404
    gifts = wl.gifts.all()
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = [f.gift for f in WishlistFacade.get_user_favorites(request.user)]
    strategy = get_template_strategy(request.user)
    return render(request, strategy.get_wishlist_template(), {
        'wishlist': wl,
        'gifts': gifts,
        'is_owner': request.user.is_authenticated and request.user == wl.owner,
        'user_favorites': user_favorites,
    })


def wishlist_by_token_view(request, token):
    """Доступ к приватному вишлисту по секретной ссылке"""
    wl = get_object_or_404(Wishlist, share_token=token)
    gifts = wl.gifts.all()
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = [f.gift for f in WishlistFacade.get_user_favorites(request.user)]
    return render(request, 'core/wishlist_detail.html', {
        'wishlist': wl,
        'gifts': gifts,
        'is_owner': request.user == wl.owner,
        'user_favorites': user_favorites,
    })


# ===== ПОДАРКИ =====

@login_required
def gift_create_view(request, wishlist_pk):
    """Создание подарка через паттерн Builder внутри Facade"""
    wl = get_object_or_404(Wishlist, pk=wishlist_pk, owner=request.user)
    form = GiftForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        gift = WishlistFacade.add_gift(
            wishlist=wl,
            name=form.cleaned_data['name'],
            category=form.cleaned_data['category'],
            price=form.cleaned_data['price'],
            priority=form.cleaned_data['priority'],
            link=form.cleaned_data.get('link', ''),
            comment=form.cleaned_data.get('comment', ''),
            image_url=form.cleaned_data.get('image_url', ''),
        )
        if 'image' in request.FILES:
            gift.image = request.FILES['image']
            gift.save()
        messages.success(request, f'Подарок "{gift.name}" добавлен!')
        return redirect('wishlist_detail', pk=wl.pk)
    return render(request, 'core/gift_form.html', {
        'form': form, 'wishlist': wl, 'action': 'create'
    })


@login_required
def gift_edit_view(request, pk):
    gift = get_object_or_404(Gift, pk=pk, wishlist__owner=request.user)
    old_name = gift.name
    form = GiftForm(request.POST or None, request.FILES or None, instance=gift)
    if request.method == 'POST' and form.is_valid():
        form.save()
        # Уведомляем дарителя если подарок был зарезервирован и название изменилось
        if gift.status == 'reserved' and gift.reserved_by and gift.name != old_name:
            event_manager.notify('gift_edited', {
                'old_name': old_name,
                'new_name': gift.name,
                'wl_title': gift.wishlist.title,
                'reserver': gift.reserved_by,
            })
        messages.success(request, 'Подарок обновлён!')
        return redirect('wishlist_detail', pk=gift.wishlist.pk)
    return render(request, 'core/gift_form.html', {
        'form': form,
        'wishlist': gift.wishlist,
        'action': 'edit',
        'gift': gift,
    })


@login_required
def gift_delete_view(request, pk):
    gift = get_object_or_404(Gift, pk=pk, wishlist__owner=request.user)
    if request.method == 'POST':
        wl_pk = gift.wishlist.pk
        # Уведомляем дарителя если подарок был зарезервирован
        if gift.status == 'reserved' and gift.reserved_by:
            event_manager.notify('gift_deleted', {
                'gift_name': gift.name,
                'wl_title': gift.wishlist.title,
                'reserver': gift.reserved_by,
            })
        gift.delete()
        messages.success(request, 'Подарок удалён.')
        return redirect('wishlist_detail', pk=wl_pk)
    return render(request, 'core/gift_confirm_delete.html', {'gift': gift})


def gift_reserve_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    gift = get_object_or_404(Gift, pk=pk)
    comment = request.POST.get('reserve_comment', '')
    reserved = WishlistFacade.reserve_gift(gift, request.user, comment)
    if reserved:
        messages.success(request, f'Вы зарезервировали «{gift.name}»!')
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('wishlist_detail', pk=gift.wishlist.pk)


def gift_unreserve_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    gift = get_object_or_404(Gift, pk=pk)
    unreserved = WishlistFacade.unreserve_gift(gift, request.user)
    if unreserved:
        messages.success(request, f'Резервирование «{gift.name}» отменено.')
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('wishlist_detail', pk=gift.wishlist.pk)


# ===== ЛИЧНЫЙ КАБИНЕТ =====

@login_required
def my_reservations_view(request):
    gifts = WishlistFacade.get_user_reservations(request.user)
    return render(request, 'core/my_reservations.html', {'gifts': gifts})


@login_required
def notifications_view(request):
    notifications = request.user.notifications.all()
    # Помечаем все как прочитанные при открытии страницы
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'core/notifications.html', {'notifications': notifications})


@login_required
def favorites_view(request):
    favorites = WishlistFacade.get_user_favorites(request.user)
    return render(request, 'core/favorites.html', {'favorites': favorites})


@login_required
def gift_favorite_toggle_view(request, pk):
    """Добавление/удаление из избранного через паттерн Command"""
    gift = get_object_or_404(Gift, pk=pk)
    is_fav = WishlistFacade.is_favorited(request.user, gift)
    if is_fav:
        WishlistFacade.remove_from_favorites(request.user, gift)
        messages.success(request, f'"{gift.name}" убран из избранного.')
    else:
        WishlistFacade.add_to_favorites(request.user, gift)
        messages.success(request, f'"{gift.name}" добавлен в избранное!')
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('wishlist_detail', pk=gift.wishlist.pk)