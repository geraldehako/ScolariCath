# notes/utils.py

from matieres.utils import get_coef_par_periode
from decimal import Decimal, ROUND_HALF_UP
from eleves.models import Eleves
from .appreciations import generer_mention, generer_appreciation

def calculer_moyenne_par_periode(eleve, periode, etablissement):
    from .models import Notes  # ← import local
    notes = Notes.objects.filter(eleve=eleve, periode=periode)
    total_points = Decimal(0)
    total_coefficients = 0

    for note in notes:
        matiere = note.matiere
        niveau = eleve.classe.niveau
        coef = get_coef_par_periode(matiere, niveau, etablissement, periode)
        total_points += note.valeur * coef
        total_coefficients += coef

    if total_coefficients == 0:
        return Decimal('0.00')

    moyenne = total_points / total_coefficients
    return moyenne.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)


def generer_bulletins_classe(classe, periode, annee_scolaire, etablissement):
    from .models import Bulletins  # ← import local
    eleves = Eleves.objects.filter(classe=classe, actif=True)

    bulletins = []
    for eleve in eleves:
        moyenne = calculer_moyenne_par_periode(eleve, periode, etablissement)
        bulletin, _ = Bulletins.objects.update_or_create(
            eleve=eleve,
            periode=periode,
            annee_scolaire=annee_scolaire,
            defaults={
                'moyenne_generale': moyenne,
                'appreciation': generer_appreciation(moyenne),
                'mention': generer_mention(moyenne),
            }
        )
        bulletin.generer_pdf()
        bulletins.append((eleve.id, moyenne))

    bulletins.sort(key=lambda x: x[1], reverse=True)
    for position, (eleve_id, _) in enumerate(bulletins, start=1):
        Bulletins.objects.filter(
            eleve__id=eleve_id, periode=periode, annee_scolaire=annee_scolaire
        ).update(rang=position)
