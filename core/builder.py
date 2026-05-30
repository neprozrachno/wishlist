from .models import Gift, Wishlist


class GiftBuilder:
    """
    Паттерн Строитель (Builder) — пошаговое создание подарка.
    Позволяет задавать только нужные параметры,
    остальные берутся по умолчанию.
    """

    def __init__(self, wishlist: Wishlist):
        self._wishlist = wishlist
        self._name = ''
        self._category = 'other'
        self._price = 0
        self._priority = 'medium'
        self._link = ''
        self._comment = ''
        self._image_url = ''

    def set_name(self, name: str) -> 'GiftBuilder':
        self._name = name
        return self

    def set_category(self, category: str) -> 'GiftBuilder':
        self._category = category
        return self

    def set_price(self, price: int) -> 'GiftBuilder':
        self._price = price
        return self

    def set_priority(self, priority: str) -> 'GiftBuilder':
        self._priority = priority
        return self

    def set_link(self, link: str) -> 'GiftBuilder':
        self._link = link
        return self

    def set_comment(self, comment: str) -> 'GiftBuilder':
        self._comment = comment
        return self

    def set_image_url(self, image_url: str) -> 'GiftBuilder':
        self._image_url = image_url
        return self

    def build(self) -> Gift:
        """Создаёт и сохраняет подарок в БД"""
        if not self._name:
            raise ValueError('Название подарка обязательно!')
        return Gift.objects.create(
            wishlist=self._wishlist,
            name=self._name,
            category=self._category,
            price=self._price,
            priority=self._priority,
            link=self._link,
            comment=self._comment,
            image_url=self._image_url,
            status='free',
        )