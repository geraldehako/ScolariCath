from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404

from authentifications.decorators import fonctionnalite_autorisee
from cores.models import AnneeScolaires, Cycles
from .models import Matieres, CoefficientMatieres, CoefficientMatieresEtablissements, CoefficientMatiereParPeriode
from .forms import MatiereEtForm, MatiereForm, CoefficientMatiereForm, CoefficientMatiereEtablissementForm, CoefficientMatiereParPeriodeForm

# === MATIERES ============================================================================================================================================
# Liste des matières
def liste_matieres(request):
    matieres = Matieres.objects.all()
    return render(request, 'backoffice/matieres/matieres/liste.html', {'matieres': matieres})

# Liste des matières pour etablissements ----------------------------
def liste_matieres_etablissementsOK(request):
    etablissement = request.user.etablissement
    cycles = etablissement.types.all()
    
    matieres_par_cycle = defaultdict(list)
    for cycle in cycles:
        matieres = Matieres.objects.filter(cycle=cycle)
        matieres_par_cycle[cycle] = matieres

    print(matieres)
    return render(request, 'frontoffice/matieres/liste_matieres.html', {
         'matieres_par_cycle': dict(matieres_par_cycle)
    })

@fonctionnalite_autorisee('liste_matieres_etablissements')  
def liste_matieres_etablissements(request):
    etablissement = request.user.etablissement
    cycles = etablissement.types.all()

    matieres_par_cycle = defaultdict(list)

    for cycle in cycles:
        # Récupère tous les niveaux de ce cycle
        niveaux = cycle.niveaux_set.all()  # ou cycle.niveaux.all() selon ta relation
        # Récupère tous les coefficients pour les niveaux de ce cycle
        coefficients = CoefficientMatieres.objects.filter(niveau__in=niveaux).select_related('matiere')

        for coef in coefficients:
            matieres_par_cycle[cycle].append({
                'matiere': coef.matiere,
                'coefficient': coef.coefficient,
                'niveau': coef.niveau
            })

    return render(request, 'frontoffice/matieres/liste_matieres.html', {
        'matieres_par_cycle': dict(matieres_par_cycle)
    })

# Ajouter une matière dans le back ------------------------------------------------------------------------
def creer_matiere(request):
    form = MatiereForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_matieres')
    return render(request, 'backoffice/matieres/matieres/formulaire.html', {'form': form})

# Ajouter une matière etablissement --------------------------------------------------------------------------
@fonctionnalite_autorisee('ajouter_matiere')   
def ajouter_matiere(request, cycle_id):
    cycle = get_object_or_404(Cycles, id=cycle_id)

    if request.method == "POST":
        form = MatiereEtForm(request.POST)
        if form.is_valid():
            matiere = form.save(commit=False)
            matiere.cycle = cycle
            matiere.save()
            return redirect('liste_matieres_etablissements')  # ou autre redirection
    else:
        form = MatiereEtForm()

    return render(request, 'frontoffice/matieres/formulaire_matiere.html', {
        'form': form,
        'cycle': cycle
    })
    
    
# Modifier une matière
def modifier_matiere(request, pk):
    matiere = get_object_or_404(Matieres, pk=pk)
    form = MatiereForm(request.POST or None, instance=matiere)
    if form.is_valid():
        form.save()
        return redirect('liste_matieres')
    return render(request, 'backoffice/matieres/matieres/formulaire.html', {'form': form})

# Supprimer une matière
def supprimer_matiere(request, pk):
    matiere = get_object_or_404(Matieres, pk=pk)
    matiere.delete()
    return redirect('liste_matieres')

# === COEFFICIENTS ============================================================================================================================================
# Liste des coefficients
def liste_coefficients(request):
    coefficients = CoefficientMatieres.objects.all()
    return render(request, 'backoffice/matieres/coefficients/liste.html', {'coefficients': coefficients})

from .models import CoefficientMatieres, Matieres, Niveaux
from .forms import CoefficientMatiereForm  # Tu dois créer ce formulaire

def ajouter_coefficient(request, matiere_id):
    matiere = Matieres.objects.get(pk=matiere_id)
    if request.method == 'POST':
        form = CoefficientMatiereForm(request.POST)
        if form.is_valid():
            coefficient = form.save(commit=False)
            coefficient.matiere = matiere
            coefficient.save()
            return redirect('liste_matieres')
    else:
        form = CoefficientMatiereForm()
    return render(request, 'backoffice/matieres/coefficients/ajouter_coefficient.html', {'form': form, 'matiere': matiere})

# Ajouter un coefficient matière
def creer_coefficient(request):
    form = CoefficientMatiereForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_coefficients')
    return render(request, 'backoffice/matieres/coefficients/formulaire.html', {'form': form})

# Modifier un coefficient matière
def modifier_coefficient(request, pk):
    coefficient = get_object_or_404(CoefficientMatieres, pk=pk)
    form = CoefficientMatiereForm(request.POST or None, instance=coefficient)
    if form.is_valid():
        form.save()
        return redirect('liste_coefficients')
    return render(request, 'backoffice/matieres/coefficients/formulaire.html', {'form': form})

# Supprimer un coefficient matière
def supprimer_coefficient(request, pk):
    coefficient = get_object_or_404(CoefficientMatieres, pk=pk)
    coefficient.delete()
    return redirect('liste_coefficients')


# === COEFFICIENT ETABLISSEMENTS ============================================================================================================================================
# Liste des coefficients par établissement
def liste_coefficients_etablissement(request):
    coefficients = CoefficientMatieresEtablissements.objects.all()
    return render(request, 'backoffice/matieres/coefficients_etablissement/liste.html', {'coefficients': coefficients})

# Ajouter un coefficient par établissement
def creer_coefficient_etablissement(request):
    form = CoefficientMatiereEtablissementForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_coefficients_etablissement')
    return render(request, 'backoffice/matieres/coefficients_etablissement/formulaire.html', {'form': form})

# Liste des coefficients par période
def liste_coefficients_periode(request):
    coefficients = CoefficientMatiereParPeriode.objects.all()
    return render(request, 'backoffice/matieres/coefficients_periode/liste.html', {'coefficients': coefficients})

# Ajouter un coefficient par période
def creer_coefficient_periode(request):
    form = CoefficientMatiereParPeriodeForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_coefficients_periode')
    return render(request, 'backoffice/matieres/coefficients_periode/formulaire.html', {'form': form})
