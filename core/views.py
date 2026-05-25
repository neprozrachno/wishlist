from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404
from .models import Wishlist, Gift
from .forms import LoginForm, RegisterForm, WishlistForm, GiftForm


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
    wishlists = request.user.wishlists.all()
    return render(request, 'core/profile.html', {
        'wishlists': wishlists,
    })


def public_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    wishlists = user.wishlists.filter(privacy='public', status='active')
    return render(request, 'core/public_profile.html', {
        'profile_user': user,
        'wishlists': wishlists,
    })


def public_feed_view(request):
    wishlists = Wishlist.objects.filter(privacy='public', status='active').select_related('owner')
    return render(request, 'core/feed.html', {
        'wishlists': wishlists,
    })


# ===== ВИШЛИСТЫ =====

@login_required
def wishlist_create_view(request):
    form = WishlistForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        wl = form.save(commit=False)
        wl.owner = request.user
        wl.save()
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
        wl.delete()
        messages.success(request, f'Вишлист «{title}» удалён.')
        return redirect('profile')
    return render(request, 'core/wishlist_confirm_delete.html', {'wishlist': wl})


def wishlist_detail_view(request, pk):
    wl = get_object_or_404(Wishlist, pk=pk)
    if wl.privacy == 'private' and wl.owner != request.user:
        raise Http404
    gifts = wl.gifts.all()
    return render(request, 'core/wishlist_detail.html', {
        'wishlist': wl,
        'gifts': gifts,
        'is_owner': request.user == wl.owner,
    })


def wishlist_by_token_view(request, token):
    wl = get_object_or_404(Wishlist, share_token=token)
    gifts = wl.gifts.all()
    return render(request, 'core/wishlist_detail.html', {
        'wishlist': wl,
        'gifts': gifts,
        'is_owner': request.user == wl.owner,
    })


# ===== ПОДАРКИ =====

@login_required
def gift_create_view(request, wishlist_pk):
    wl = get_object_or_404(Wishlist, pk=wishlist_pk, owner=request.user)
    form = GiftForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        gift = form.save(commit=False)
        gift.wishlist = wl
        gift.save()
        messages.success(request, f'Подарок «{gift.name}» добавлен!')
        return redirect('wishlist_detail', pk=wl.pk)
    return render(request, 'core/gift_form.html', {'form': form, 'wishlist': wl, 'action': 'create'})


@login_required
def gift_edit_view(request, pk):
    gift = get_object_or_404(Gift, pk=pk, wishlist__owner=request.user)
    form = GiftForm(request.POST or None, request.FILES or None, instance=gift)
    if request.method == 'POST' and form.is_valid():
        form.save()
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
        gift.delete()
        messages.success(request, 'Подарок удалён.')
        return redirect('wishlist_detail', pk=wl_pk)
    return render(request, 'core/gift_confirm_delete.html', {'gift': gift})


def gift_reserve_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    gift = get_object_or_404(Gift, pk=pk)
    if gift.status == 'free':
        comment = request.POST.get('reserve_comment', '')
        gift.status = 'reserved'
        gift.reserved_by = request.user
        gift.reserve_comment = comment
        gift.save()
        messages.success(request, f'Вы зарезервировали «{gift.name}»!')
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('wishlist_detail', pk=gift.wishlist.pk)

def gift_unreserve_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    gift = get_object_or_404(Gift, pk=pk)
    if gift.status == 'reserved' and gift.reserved_by == request.user:
        gift.status = 'free'
        gift.reserved_by = None
        gift.save()
        messages.success(request, f'Резервирование «{gift.name}» отменено.')
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('wishlist_detail', pk=gift.wishlist.pk)

@login_required
def my_reservations_view(request):
    gifts = Gift.objects.filter(
        reserved_by=request.user
    ).select_related('wishlist', 'wishlist__owner')
    return render(request, 'core/my_reservations.html', {'gifts': gifts})