from django.contrib.auth.models import User
from .models import Wishlist, Gift
import secrets


class WishlistFacade:
    """
    Паттерн Фасад (Facade) — скрывает сложную логику работы
    с вишлистами, подарками и избранным за простым интерфейсом.
    Все views работают через фасад, не обращаясь к моделям напрямую.
    """

    # ===== ВИШЛИСТЫ =====

    @staticmethod
    def create_wishlist(owner: User, title: str, event_type: str = 'birthday',
                        event_date=None, privacy: str = 'public', comment: str = '') -> Wishlist:
        """Создаёт новый вишлист с уникальным share_token"""
        wishlist = Wishlist.objects.create(
            owner=owner,
            title=title,
            event_type=event_type,
            event_date=event_date,
            privacy=privacy,
            comment=comment,
            share_token=secrets.token_urlsafe(32),
        )
        return wishlist

    @staticmethod
    def get_user_wishlists(user: User):
        """Возвращает все вишлисты пользователя"""
        return Wishlist.objects.filter(owner=user)

    @staticmethod
    def get_public_wishlists():
        """Возвращает все активные публичные вишлисты"""
        return Wishlist.objects.filter(privacy='public', status='active').select_related('owner')

    @staticmethod
    def delete_wishlist(wishlist: Wishlist) -> None:
        """Удаляет вишлист вместе со всеми подарками"""
        wishlist.gifts.all().delete()
        wishlist.delete()

    # ===== ПОДАРКИ =====

    @staticmethod
    def add_gift(wishlist: Wishlist, name: str, category: str = 'other',
                 price: int = 0, priority: str = 'medium',
                 link: str = '', comment: str = '', image_url: str = '') -> Gift:
        """Добавляет подарок в вишлист через паттерн Builder"""
        from .builder import GiftBuilder
        return GiftBuilder(wishlist) \
            .set_name(name) \
            .set_category(category) \
            .set_price(price) \
            .set_priority(priority) \
            .set_link(link) \
            .set_comment(comment) \
            .set_image_url(image_url) \
            .build()

    @staticmethod
    def reserve_gift(gift: Gift, user: User, comment: str = '') -> bool:
        """Резервирует подарок и уведомляет владельца через Observer"""
        if gift.status != 'free':
            return False
        gift.status = 'reserved'
        gift.reserved_by = user
        gift.reserve_comment = comment
        gift.save()

        from .observer import event_manager
        event_manager.notify('gift_reserved', {
            'gift': gift,
            'reserver': user,
        })

        wishlist = gift.wishlist
        if not wishlist.gifts.filter(status='free').exists():
            event_manager.notify('all_gifts_reserved', {
                'wl_title': wishlist.title,
                'owner': wishlist.owner,
            })

        return True

    @staticmethod
    def unreserve_gift(gift: Gift, user: User) -> bool:
        """Отменяет резервирование и уведомляет владельца через Observer"""
        if gift.status != 'reserved' or gift.reserved_by != user:
            return False
        gift.status = 'free'
        gift.reserved_by = None
        gift.reserve_comment = ''
        gift.save()

        from .observer import event_manager
        event_manager.notify('gift_unreserved', {
            'gift': gift,
            'reserver': user,
        })

        return True

    @staticmethod
    def get_user_reservations(user: User):
        """Возвращает все подарки зарезервированные пользователем"""
        return Gift.objects.filter(
            reserved_by=user
        ).select_related('wishlist', 'wishlist__owner')

    @staticmethod
    def get_wishlist_stats(wishlist: Wishlist) -> dict:
        """Возвращает статистику вишлиста — счётчики и прогресс"""
        gifts = wishlist.gifts.all()
        total = gifts.count()
        reserved = gifts.filter(status='reserved').count()
        gifted = gifts.filter(status='gifted').count()
        free = gifts.filter(status='free').count()
        return {
            'total': total,
            'reserved': reserved,
            'gifted': gifted,
            'free': free,
            'progress': round((reserved + gifted) / total * 100) if total > 0 else 0,
        }

    # ===== ИЗБРАННОЕ =====

    @staticmethod
    def add_to_favorites(user, gift) -> bool:
        from .models import Favorite
        favorite, created = Favorite.objects.get_or_create(user=user, gift=gift)
        return created

    @staticmethod
    def remove_from_favorites(user, gift) -> bool:
        from .models import Favorite
        deleted, _ = Favorite.objects.filter(user=user, gift=gift).delete()
        return bool(deleted)

    @staticmethod
    def get_user_favorites(user):
        """Возвращает все избранные подарки пользователя"""
        from .models import Favorite
        return Favorite.objects.filter(user=user).select_related('gift', 'gift__wishlist')

    @staticmethod
    def is_favorited(user, gift) -> bool:
        """Проверяет есть ли подарок в избранном у пользователя"""
        from .models import Favorite
        return Favorite.objects.filter(user=user, gift=gift).exists()