from authentifications.models import AccesFonctionnalites

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

def fonctionnalite_autorisee(fonctionnalite):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            utilisateur = request.user
            if not utilisateur.is_authenticated:
                messages.error(request, "Veuillez vous connecter pour accéder à cette page.")
                return redirect(reverse("login"))

            if utilisateur.role and AccesFonctionnalites.objects.filter(
                role=utilisateur.role,
                code=fonctionnalite,
                autorise=True
            ).exists():
                return view_func(request, *args, **kwargs)

            messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")

            # Redirection selon le rôle
            if utilisateur.role and utilisateur.role.nom in ['Administrateur', 'Trésorerie', 'Secrétaire Exécutif', 'Comptabilité'] :
                return redirect("accueil_back")
            if utilisateur.role and utilisateur.role.nom in ['Direction', 'Économat']:
                return redirect("accueil")

            return redirect("no_access")  # fallback général

        return _wrapped_view
    return decorator

# decorators.py
def fonctionnalite_autoriseeBon(fonctionnalite):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            utilisateur = request.user
            if not utilisateur.is_authenticated:
                messages.error(request, "Veuillez vous connecter pour accéder à cette page.")
                return redirect(reverse("login"))  # Assure-toi que "login" est bien le nom de ton URL de connexion

            if utilisateur.role and AccesFonctionnalites.objects.filter(
                role=utilisateur.role,
                #fonctionnalite=fonctionnalite,
                code=fonctionnalite,
                autorise=True
            ).exists():
                return view_func(request, *args, **kwargs)

            messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")
            return redirect("accueil")  # ou une page d'erreur personnalisée
        return _wrapped_view
    return decorator

# def fonctionnalite_autorisee(code_fonction):
#     def decorator(view_func):
#         @wraps(view_func)
#         def _wrapped_view(request, *args, **kwargs):
#             user = request.user
#             if user.is_authenticated and user.role:
#                 acces = AccesFonctionnalites.objects.filter(
#                     role=user.role,
#                     code=code_fonction,
#                     autorise=True
#                 ).exists()
#                 if acces:
#                     return view_func(request, *args, **kwargs)
#             return redirect('no_access')
#         return _wrapped_view
#     return decorator
