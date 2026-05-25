from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Wishlist, Gift


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'placeholder': 'neprozrachno'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='E-mail', required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Повторите пароль'
        for field in self.fields.values():
            field.help_text = None


class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['title', 'comment', 'event_type', 'event_date', 'privacy']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Например: День Рождения, Новый год'
            }),
            'comment': forms.Textarea(attrs={
                'placeholder': 'Напиши что-нибудь своим друзьям...',
                'rows': 4,
            }),
            'event_date': forms.DateInput(attrs={
                'type': 'date',
                'placeholder': 'Выберите дату'
            }),
            'privacy': forms.Select(choices=[
                ('public', 'Публичный — подборка для вдохновения'),
                ('private', 'Приватный — для друзей по ссылке'),
            ]),
        }
        labels = {
            'title':      'Название вишлиста',
            'comment':    'Комментарий',
            'event_type': 'Тип события',
            'event_date': 'Дата события',
            'privacy':    'Приватность',
        }


class GiftForm(forms.ModelForm):
    class Meta:
        model = Gift
        fields = ['name', 'category', 'price', 'priority', 'link', 'image', 'image_url', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Например: наушники AirPods Pro'
            }),
            'price': forms.NumberInput(attrs={
                'placeholder': '0', 'min': '0'
            }),
            'link': forms.URLInput(attrs={
                'placeholder': 'https://market.yandex.ru/...'
            }),
            'comment': forms.Textarea(attrs={
                'placeholder': 'Уточни какие-то детали подарка...',
                'rows': 3,
            }),
            'image_url': forms.URLInput(attrs={
                'placeholder': 'Или вставь ссылку на товар — картинка подтянется сама'
            }),
        }
        labels = {
            'name':     'Название',
            'category': 'Категория',
            'price':    'Цена (₽)',
            'priority': 'Приоритет',
            'link':     'Ссылка на подарок',
            'comment':  'Комментарий к подарку',
        }
