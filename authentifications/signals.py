# signals.py
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import HistoriqueConnexion
from .utils import get_client_ip

@receiver(user_logged_in)
def enregistrer_connexion(sender, request, user, **kwargs):
    HistoriqueConnexion.objects.create(
        utilisateur=user,
        type_evenement='connexion',
        adresse_ip=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

@receiver(user_logged_out)
def enregistrer_deconnexionBON(sender, request, user, **kwargs):
    if user.is_authenticated:
        HistoriqueConnexion.objects.create(
            utilisateur=user,
            type_evenement='deconnexion',
            adresse_ip=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

@receiver(user_logged_out)
def enregistrer_deconnexion(sender, request, user, **kwargs):
    if user and user.is_authenticated:
        HistoriqueConnexion.objects.create(
            utilisateur=user,
            type_evenement='deconnexion',
            adresse_ip=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
