from django import template
from datetime import date

register = template.Library()

@register.filter
def days_until(value):
    if not value:
        return None
    today = date.today()
    delta = (value - today).days
    return delta