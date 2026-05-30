from abc import ABC, abstractmethod


class BaseObserver(ABC):
    """Паттерн Наблюдатель (Observer) — базовый класс наблюдателя"""

    @abstractmethod
    def update(self, event_type: str, data: dict) -> None:
        pass


class BasePublisher(ABC):
    """Базовый класс издателя — определяет интерфейс управления наблюдателями"""

    @abstractmethod
    def subscribe(self, observer: BaseObserver) -> None:
        pass

    @abstractmethod
    def unsubscribe(self, observer: BaseObserver) -> None:
        pass

    @abstractmethod
    def notify(self, event_type: str, data: dict) -> None:
        pass


class NotificationObserver(BaseObserver):
    """
    Наблюдатель — создаёт уведомления в БД при наступлении событий.
    Подписан на: gift_reserved, gift_unreserved.
    Владелец вишлиста не узнаёт кто именно зарезервировал.
    """

    def update(self, event_type: str, data: dict) -> None:
        if event_type == 'gift_reserved':
            self._on_gift_reserved(data)
        elif event_type == 'gift_unreserved':
            self._on_gift_unreserved(data)
        elif event_type == 'gift_deleted':
            self._on_gift_deleted(data)
        elif event_type == 'gift_edited':
            self._on_gift_edited(data)
        elif event_type == 'wishlist_deleted':
            self._on_wishlist_deleted(data)
        elif event_type == 'all_gifts_reserved':
            self._on_all_gifts_reserved(data)

    def _on_gift_reserved(self, data: dict) -> None:
        from .models import Notification
        gift = data['gift']
        name = gift.name
        wl_title = gift.wishlist.title
        comment = gift.reserve_comment
        msg = f'🎁 Кто-то зарезервировал подарок "{name}" из вишлиста "{wl_title}"!'
        if comment:
            msg += f' Комментарий: {comment}'
        Notification.objects.create(
            recipient=gift.wishlist.owner,
            message=msg
        )

    def _on_gift_unreserved(self, data: dict) -> None:
        from .models import Notification
        gift = data['gift']
        name = gift.name
        wl_title = gift.wishlist.title
        Notification.objects.create(
            recipient=gift.wishlist.owner,
            message=f'❌ Резервирование подарка "{name}" из вишлиста "{wl_title}" отменено.'
        )

    def _on_gift_deleted(self, data: dict) -> None:
        from .models import Notification
        gift_name = data['gift_name']
        wl_title = data['wl_title']
        user = data['reserver']
        Notification.objects.create(
            recipient=user,
            message=f'❌ Подарок "{gift_name}" из вишлиста "{wl_title}" был удалён — резервирование снято.'
        )

    def _on_gift_edited(self, data: dict) -> None:
        from .models import Notification
        old_name = data['old_name']
        new_name = data['new_name']
        wl_title = data['wl_title']
        reserver = data['reserver']
        Notification.objects.create(
            recipient=reserver,
            message=f'✏️ Подарок "{old_name}" из вишлиста "{wl_title}" был изменён на "{new_name}". Проверь актуальность резервирования!'
        )

    def _on_wishlist_deleted(self, data: dict) -> None:
        from .models import Notification
        Notification.objects.create(
            recipient=data['reserver'],
            message=f'🗑️ Вишлист "{data["wl_title"]}" был удалён. Твоё резервирование подарка "{data["gift_name"]}" снято.'
        )

    def _on_all_gifts_reserved(self, data: dict) -> None:
        from .models import Notification
        wl_title = data['wl_title']
        owner = data['owner']
        Notification.objects.create(
            recipient=owner,
            message=f'🎉 Все подарки в вишлисте "{wl_title}" зарезервированы!'
        )


class EventManager(BasePublisher):
    """
    Менеджер событий — реализует интерфейс издателя.
    Хранит список наблюдателей и оповещает их при наступлении событий.
    """

    def __init__(self):
        self._observers: list[BaseObserver] = []

    def subscribe(self, observer: BaseObserver) -> None:
        """Подписывает наблюдателя на события"""
        self._observers.append(observer)

    def unsubscribe(self, observer: BaseObserver) -> None:
        """Отписывает наблюдателя от событий"""
        self._observers.remove(observer)

    def notify(self, event_type: str, data: dict) -> None:
        """Оповещает всех наблюдателей о наступлении события"""
        for observer in self._observers:
            observer.update(event_type, data)


# Глобальный менеджер событий с подключённым наблюдателем уведомлений
event_manager = EventManager()
event_manager.subscribe(NotificationObserver())