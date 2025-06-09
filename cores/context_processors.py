from .models import AnneeScolaires

def annee_scolaire_active(request):
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    return {
        'annee_scolaire_active': annee_active
    }
