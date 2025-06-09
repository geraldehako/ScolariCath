from authentifications.models import AccesFonctionnalites, Roles
from authentifications.constantes import FONCTIONNALITES_PAR_DEFAUT, FONCTIONNALITES_PAR_ROLE  # ou adapte l'import

def assigner_fonctionnalites_par_defautOK(role: Roles):
    for fonctionnalite in FONCTIONNALITES_PAR_DEFAUT:
        AccesFonctionnalites.objects.get_or_create(
            role=role,
            fonctionnalite=fonctionnalite,
            defaults={"autorise": True}  # ou False selon le rôle
        )

def assigner_fonctionnalites_par_defaut(role: Roles):
    nom_role = role.nom.strip()

    # Récupération des fonctionnalités du rôle, ou une liste vide si inconnu
    liste_fonctionnalites = FONCTIONNALITES_PAR_ROLE.get(nom_role, [])

    for f in liste_fonctionnalites:
        AccesFonctionnalites.objects.get_or_create(
            role=role,
            code=f["code"],
            defaults={"fonctionnalite": f["fonctionnalite"], "autorise": True}
        )