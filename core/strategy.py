from abc import ABC, abstractmethod


class BaseTemplateStrategy(ABC):
    """
    Паттерн Стратегия (Strategy) — выбор шаблона в зависимости
    от типа пользователя (авторизованный / гость).
    Позволяет показывать разный UI без изменения логики views.
    """

    @abstractmethod
    def get_feed_template(self) -> str:
        pass

    @abstractmethod
    def get_wishlist_template(self) -> str:
        pass


class AuthenticatedStrategy(BaseTemplateStrategy):
    """Стратегия для авторизованного пользователя — полный UI с сайдбаром"""

    def get_feed_template(self) -> str:
        return 'core/feed.html'

    def get_wishlist_template(self) -> str:
        return 'core/wishlist_detail.html'


class GuestStrategy(BaseTemplateStrategy):
    """Стратегия для гостя — упрощённый UI без сайдбара, с призывом войти"""

    def get_feed_template(self) -> str:
        return 'core/feed_guest.html'

    def get_wishlist_template(self) -> str:
        return 'core/wishlist_detail_guest.html'


def get_template_strategy(user) -> BaseTemplateStrategy:
    """Фабричная функция — возвращает нужную стратегию по типу пользователя"""
    if user.is_authenticated:
        return AuthenticatedStrategy()
    return GuestStrategy()