# matieres/utils.py

from .models import CoefficientMatiereParPeriode, CoefficientMatieresEtablissements

def get_coefficient(matiere, niveau, etablissement):
    try:
        return CoefficientMatieresEtablissements.objects.get(
            matiere=matiere,
            niveau=niveau,
            etablissement=etablissement
        ).coefficient
    except CoefficientMatieresEtablissements.DoesNotExist:
        return 1  # valeur par défaut

def get_coef_par_periode(matiere, niveau, etablissement, periode):
    try:
        return CoefficientMatiereParPeriode.objects.get(
            matiere=matiere,
            niveau=niveau,
            etablissement=etablissement,
            periode=periode
        ).coefficient
    except CoefficientMatiereParPeriode.DoesNotExist:
        return get_coefficient(matiere, niveau, etablissement)
