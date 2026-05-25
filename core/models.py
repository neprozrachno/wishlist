from django.db import models
from django.contrib.auth.models import User
import secrets


class Wishlist(models.Model):
    EVENT_TYPES = [
        ('birthday',    'День Рождения'),
        ('newyear',     'Новый Год'),
        ('wedding',     'Свадьба'),
        ('holiday',     'Праздник'),
        ('noreason',    'Без повода'),
    ]
    PRIVACY_CHOICES = [
        ('public',  'Публичный'),
        ('private', 'Приватный'),
    ]
    STATUS_CHOICES = [
        ('active',    'Активный'),
        ('finished',  'Завершён'),
        ('archived',  'Архивный'),
    ]

    owner      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    title      = models.CharField('Название', max_length=200)
    comment    = models.TextField('Комментарий', blank=True)
    event_type = models.CharField('Тип события', max_length=20, choices=EVENT_TYPES, default='birthday')
    event_date = models.DateField('Дата события', null=True, blank=True)
    privacy    = models.CharField('Приватность', max_length=10, choices=PRIVACY_CHOICES, default='public')
    status     = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='active')
    share_token = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.share_token:
            self.share_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} ({self.owner.username})'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Вишлист'
        verbose_name_plural = 'Вишлисты'


class Gift(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Электроника'),
        ('books',       'Книги'),
        ('clothes',     'Одежда'),
        ('home',        'Дом'),
        ('toys',        'Игрушки'),
        ('certificate', 'Сертификат'),
        ('other',       'Другое'),
    ]
    PRIORITY_CHOICES = [
        ('low',    'Низкий'),
        ('medium', 'Средний'),
        ('high',   'Высокий'),
    ]
    STATUS_CHOICES = [
        ('free',     'Свободен'),
        ('reserved', 'Зарезервирован'),
        ('gifted',   'Подарен'),
    ]

    wishlist    = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='gifts')
    name        = models.CharField('Название', max_length=200)
    category    = models.CharField('Категория', max_length=20, choices=CATEGORY_CHOICES, default='other')
    price       = models.PositiveIntegerField('Цена (₽)', default=0)
    priority    = models.CharField('Приоритет', max_length=10, choices=PRIORITY_CHOICES, default='medium')
    link        = models.URLField('Ссылка', blank=True)
    image = models.ImageField('Изображение', upload_to='gifts/', null=True, blank=True)
    image_url = models.URLField('URL изображения', blank=True)
    comment     = models.TextField('Комментарий', blank=True)
    status      = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='free')
    reserved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reserved_gifts')
    reserve_comment = models.TextField('Комментарий дарителя', blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} → {self.wishlist.title}'

    class Meta:
        ordering = ['-priority', 'name']
        verbose_name = 'Подарок'
        verbose_name_plural = 'Подарки'
