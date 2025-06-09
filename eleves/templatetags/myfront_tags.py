# eleves/templatetags/myfront_tags.py
from django import template

register = template.Library()

@register.filter
def get_item(d, key):
    try:
        return d.get(key, 0)
    except Exception:
        return 0  # Sécurité contre erreurs si d n’est pas un dict



@register.filter
def get_dict(d, key):
    if isinstance(d, dict):
        return d.get(key, {})
    return {}

@register.filter
def get_nested_value(d, key):
    if isinstance(d, dict):
        return d.get(key, 0)
    return 0
