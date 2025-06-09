# ton_app/templatetags/utils.py
from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def index(sequence, position):
    try:
        return sequence[position]
    except:
        return None
