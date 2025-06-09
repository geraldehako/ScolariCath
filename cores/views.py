from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cycles, AnneeScolaires, Trimestres, Periodes
from .forms import CycleForm, AnneeScolaireForm, TrimestreForm, PeriodeForm

# Cycle =============================================================================================================================================================
def liste_cycles(request):
    cycles = Cycles.objects.all()
    return render(request, 'backoffice/gestions/cycles/liste_cycles.html', {'cycles': cycles})

def ajouter_cycle(request):
    form = CycleForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_cycles')
    return render(request, 'backoffice/gestions/cycles/formulaire.html', {'form': form, 'titre': 'Ajouter Cycle'})

def modifier_cycle(request, pk):
    cycle = get_object_or_404(Cycles, pk=pk)
    form = CycleForm(request.POST or None, instance=cycle)
    if form.is_valid():
        form.save()
        return redirect('liste_cycles')
    return render(request, 'backoffice/gestions/cycles/formulaire.html', {'form': form, 'titre': 'Modifier Cycle'})

def supprimer_cycle(request, pk):
    cycle = get_object_or_404(Cycles, pk=pk)
    if request.method == "POST":
        cycle.delete()
        return redirect('liste_cycles')
    return render(request, 'backoffice/gestions/cycles/confirm_delete.html', {'objet': cycle, 'titre': 'Supprimer Cycle'})


# Annee scolaire ================================================================================================================================================
# ANNEE SCOLAIRE
def liste_annees_scolaires(request):
    annees_scolaires = AnneeScolaires.objects.all()
    return render(request, 'backoffice/gestions/annees scolaires/liste_annees_scolaires.html', {'annees_scolaires': annees_scolaires})

def ajouter_annee_scolaire(request):
    form = AnneeScolaireForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_annees_scolaires')
    return render(request, 'backoffice/gestions/annees scolaires/formulaire.html', {'form': form, 'titre': 'Ajouter Année Scolaire'})

def modifier_annee_scolaire(request, pk):
    annee_scolaire = get_object_or_404(AnneeScolaires, pk=pk)
    form = AnneeScolaireForm(request.POST or None, instance=annee_scolaire)
    if form.is_valid():
        form.save()
        return redirect('liste_annees_scolaires')
    return render(request, 'backoffice/gestions/annees scolaires/formulaire.html', {'form': form, 'titre': 'Modifier Année Scolaire'})

def supprimer_annee_scolaire(request, pk):
    annee_scolaire = get_object_or_404(AnneeScolaires, pk=pk)
    if request.method == 'POST':
        annee_scolaire.delete()
        return redirect('liste_annees_scolaires')
    return render(request, 'backoffice/gestions/annees scolaires/confirm_delete.html', {'objet': annee_scolaire})

def generer_trimestres(request, pk):
    annee = get_object_or_404(AnneeScolaires, pk=pk)

    if Periodes.objects.filter(annee_scolaire=annee).exists():
        messages.warning(request, "Les périodes ont déjà été générées pour cette année.")
    else:
        annee.generer_trimestres()
        messages.success(request, "Trimestres et périodes générés avec succès.")

    return redirect('liste_annees_scolaires')


def activer_annee_scolaire(request, pk):
    annee_scolaire = get_object_or_404(AnneeScolaires, pk=pk)
    
    # Désactiver toutes les autres années scolaires
    AnneeScolaires.objects.update(active=False)
    
    # Activer l'année scolaire spécifique
    annee_scolaire.active = True
    annee_scolaire.save()

    return redirect('liste_annees_scolaires')

# TRIMESTRES =============================================================================================================================================================
def liste_trimestres(request):
    trimestres = Trimestres.objects.all()
    return render(request, 'backoffice/gestions/trimestres/liste_trimestres.html', {'trimestres': trimestres})

def ajouter_trimestre(request):
    form = TrimestreForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_trimestres')
    return render(request, 'backoffice/gestions/trimestres/formulaire.html', {'form': form, 'titre': 'Ajouter Trimestre'})

def modifier_trimestre(request, pk):
    trimestre = get_object_or_404(Trimestres, pk=pk)
    form = TrimestreForm(request.POST or None, instance=trimestre)
    if form.is_valid():
        form.save()
        return redirect('liste_trimestres')
    return render(request, 'backoffice/gestions/trimestres/formulaire.html', {'form': form, 'titre': 'Modifier Trimestre'})

def supprimer_trimestre(request, pk):
    trimestre = get_object_or_404(Trimestres, pk=pk)
    if request.method == 'POST':
        trimestre.delete()
        return redirect('liste_trimestres')
    return render(request, 'backoffice/gestions/trimestres/confirm_delete.html', {'objet': trimestre})


# PERIODES ==============================================================================================================================================================
def liste_periodes(request):
    periodes = Periodes.objects.all()
    return render(request, 'backoffice/gestions/periodes/liste_periodes.html', {'periodes': periodes})

def ajouter_periode(request):
    form = PeriodeForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_periodes')
    return render(request, 'backoffice/gestions/periodes/formulaire.html', {'form': form, 'titre': 'Ajouter Période'})

def modifier_periode(request, pk):
    periode = get_object_or_404(Periodes, pk=pk)
    form = PeriodeForm(request.POST or None, instance=periode)
    if form.is_valid():
        form.save()
        return redirect('liste_periodes')
    return render(request, 'backoffice/gestions/periodes/formulaire.html', {'form': form, 'titre': 'Modifier Période'})

def supprimer_periode(request, pk):
    periode = get_object_or_404(Periodes, pk=pk)
    if request.method == 'POST':
        periode.delete()
        return redirect('liste_periodes')
    return render(request, 'backoffice/gestions/periodes/confirm_delete.html', {'objet': periode})