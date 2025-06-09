# eleves/templatetags/my_tags.py
from django import template

register = template.Library()

@register.filter
def get_dict(d, key):
    """Accès sécurisé à un dictionnaire : d.get(key, {})"""
    if isinstance(d, dict):
        return d.get(key, {})
    return {}

@register.filter
def get_nested_value(d, key):
    """Retourne d.get(key, 0) si d est un dictionnaire, sinon retourne 0"""
    if isinstance(d, dict):
        return d.get(key, 0)
    return 0


