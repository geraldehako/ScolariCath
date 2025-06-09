from django import forms
from django.shortcuts import get_object_or_404, render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from authentifications.decorators import fonctionnalite_autorisee
from cores.models import Periodes
from eleves.models import Eleves
from etablissements.models import Classes
from matieres.models import Matieres
from notes.forms import SelectionMatierePeriodeForm, TypeEvaluationForm
from django.forms import modelform_factory

from notes.models import Notes, TypeEvaluation

def liste_type_evaluations(request):
    types = TypeEvaluation.objects.all()
    return render(request, 'backoffice/notes/type_evaluation/liste.html', {'types': types})

def creer_type_evaluation(request):
    form = TypeEvaluationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_type_evaluations')
    return render(request, 'backoffice/notes/type_evaluation/formulaire.html', {'form': form, 'titre': 'Créer un type d\'évaluation'})

def modifier_type_evaluation(request, pk):
    type_eval = get_object_or_404(TypeEvaluation, pk=pk)
    form = TypeEvaluationForm(request.POST or None, instance=type_eval)
    if form.is_valid():
        form.save()
        return redirect('liste_type_evaluations')
    return render(request, 'backoffice/notes/type_evaluation/formulaire.html', {'form': form, 'titre': 'Modifier le type d\'évaluation'})

def supprimer_type_evaluation(request, pk):
    type_eval = get_object_or_404(TypeEvaluation, pk=pk)
    if request.method == 'POST':
        type_eval.delete()
        return redirect('liste_type_evaluations')
    return render(request, 'backoffice/notes/type_evaluation/confirm_delete.html', {'objet': type_eval})

def selectionner_matiere_periodeBON(request, classe_id):
    classe = Classes.objects.get(id=classe_id)
    niveau_id = classe.niveau.id

    if request.method == 'POST':
        form = SelectionMatierePeriodeForm(request.POST, niveau_id=niveau_id)
        if form.is_valid():
            matiere = form.cleaned_data['matiere']
            periode = form.cleaned_data['periode']
            return redirect('ajouter_notes_classe', classe_id=classe.id, matiere_id=matiere.id, periode_id=periode.id)
    else:
        form = SelectionMatierePeriodeForm(niveau_id=niveau_id)

    return render(request, 'frontoffice/notes/selection_matiere_periode.html', {
        'form': form,
        'classe': classe,
    })

@fonctionnalite_autorisee('selectionner_matiere_periode')
def selectionner_matiere_periode(request, classe_id):
    classe = Classes.objects.get(id=classe_id)
    niveau = classe.niveau
    niveau_id = niveau.id
    cycle_id = niveau.cycle.id  # 🔹 Récupération du cycle associé au niveau

    if request.method == 'POST':
        form = SelectionMatierePeriodeForm(request.POST, niveau_id=niveau_id, cycle_id=cycle_id)
        if form.is_valid():
            matiere = form.cleaned_data['matiere']
            periode = form.cleaned_data['periode']
            return redirect('ajouter_notes_classe', classe_id=classe.id, matiere_id=matiere.id, periode_id=periode.id)
    else:
        form = SelectionMatierePeriodeForm(niveau_id=niveau_id, cycle_id=cycle_id)

    return render(request, 'frontoffice/notes/selection_matiere_periode.html', {
        'form': form,
        'classe': classe,
    })



def ajouter_notes_classeT(request, classe_id, matiere_id, periode_id):
    classe = Classes.objects.get(id=classe_id)
    matiere = Matieres.objects.get(id=matiere_id)
    periode = Periodes.objects.get(id=periode_id)
    types_evaluation = TypeEvaluation.objects.all()
    
    eleves = Eleves.objects.filter(inscriptions__classe=classe).distinct()

    # Générer un queryset vide (pour 5 notes x nombre d'élèves)
    total_notes = 5 * eleves.count()

    NoteFormSet = modelform_factory(Notes, fields=('valeur',), widgets={
        'valeur': forms.NumberInput(attrs={'class': 'form-control'})
    })

    if request.method == 'POST':
        form_data = request.POST
        for eleve in eleves:
            for i in range(5):
                valeur = form_data.get(f'note_{eleve.id}_{i}')
                if valeur:
                    Notes.objects.create(
                        eleve=eleve,
                        matiere=matiere,
                        periode=periode,
                        enseignant=None,  # ou l'enseignant connecté
                        valeur=valeur,
                        bareme=20  # ou ajustable si tu veux
                    )
        return redirect('liste_notes_classe')  # à adapter
    return render(request, 'frontoffice/notes/ajouter_notes_classe.html', {
        'classe': classe,
        'matiere': matiere,
        'periode': periode,
        'eleves': eleves,
        'range_5': range(5),  # pour itérer 5 fois par élève
        'types_evaluation': types_evaluation,
    })

@fonctionnalite_autorisee('voir_notes_classe')
def voir_notes_classe(request, classe_id, matiere_id, periode_id):
    classe = Classes.objects.get(id=classe_id)
    matiere = Matieres.objects.get(id=matiere_id)
    periode = Periodes.objects.get(id=periode_id)
    
    eleves = Eleves.objects.filter(inscriptions__classe=classe).distinct()

    notes = Notes.objects.filter(eleve__in=eleves, matiere=matiere, periode=periode)

    return render(request, 'frontoffice/notes/liste_notes_classe.html', {
        'classe': classe,
        'matiere': matiere,
        'periode': periode,
        'notes': notes,
    })


def ajouter_notes_classe(request, classe_id, matiere_id, periode_id):
    classe = get_object_or_404(Classes, id=classe_id)
    matiere = get_object_or_404(Matieres, id=matiere_id)
    periode = get_object_or_404(Periodes, id=periode_id)
    types_evaluation = TypeEvaluation.objects.all()
    
    eleves = Eleves.objects.filter(inscriptions__classe=classe).distinct()

    if request.method == 'POST':
        for eleve in eleves:
            for i in range(5):
                note_key = f'note_{eleve.id}_{i}'
                type_key = f'type_{eleve.id}_{i}'

                valeur = request.POST.get(note_key)
                type_eval_id = request.POST.get(type_key)

                if valeur and type_eval_id:
                    try:
                        type_eval = TypeEvaluation.objects.get(id=type_eval_id)
                        Notes.objects.create(
                            eleve=eleve,
                            matiere=matiere,
                            periode=periode,
                            enseignant=getattr(request.user, 'enseignants', None),
                            valeur=valeur,
                            type_evaluation=type_eval
                        )
                    except TypeEvaluation.DoesNotExist:
                        continue  # Ignore les erreurs de type évaluation invalides
        messages.success(request, "Les notes ont été enregistrées avec succès.")
        return redirect('liste_eleves_inscrits')  # 🔁 À adapter selon ta vue

    return render(request, 'frontoffice/notes/ajouter_notes_classe.html', {
        'classe': classe,
        'matiere': matiere,
        'periode': periode,
        'eleves': eleves,
        'range_5': range(5),
        'types_evaluation': types_evaluation,
    })


def modifier_notes_classeO(request, classe_id, matiere_id, periode_id):
    classe = get_object_or_404(Classes, id=classe_id)
    matiere = get_object_or_404(Matieres, id=matiere_id)
    periode = get_object_or_404(Periodes, id=periode_id)
    types_evaluation = TypeEvaluation.objects.all()

    eleves = Eleves.objects.filter(inscriptions__classe=classe).distinct()

    if request.method == 'POST':
        for eleve in eleves:
            for i in range(5):
                note_id = request.POST.get(f'note_id_{eleve.id}_{i}')
                valeur = request.POST.get(f'note_{eleve.id}_{i}')
                type_eval_id = request.POST.get(f'type_eval_{eleve.id}_{i}')

                if valeur and type_eval_id:
                    type_eval = TypeEvaluation.objects.get(id=type_eval_id)

                    if note_id:
                        # Modifier la note existante
                        note = Notes.objects.get(id=note_id)
                        note.valeur = valeur
                        note.type_evaluation = type_eval
                        note.save()

        return redirect('liste_notes_classe')  # à adapter selon ton URL

    # Préparer les notes existantes
    notes_dict = {}
    for eleve in eleves:
        notes = Notes.objects.filter(
            eleve=eleve, matiere=matiere, periode=periode
        ).order_by('id')[:5]  # limite à 5
        notes_dict[eleve.id] = list(notes)

    return render(request, 'frontoffice/notes/modifier_notes_classe.html', {
        'classe': classe,
        'matiere': matiere,
        'periode': periode,
        'eleves': eleves,
        'notes_dict': notes_dict,
        'range_5': range(5),
        'types_evaluation': types_evaluation,
    })


def modifier_notes_classe1(request, classe_id, matiere_id, periode_id):
    classe = get_object_or_404(Classes, id=classe_id)
    matiere = get_object_or_404(Matieres, id=matiere_id)
    periode = get_object_or_404(Periodes, id=periode_id)
    eleves = Eleves.objects.filter(inscriptions__classe=classe).distinct()
    types_evaluation = TypeEvaluation.objects.all()

    # dictionnaire : { eleve_id: [note1, note2, ..., note5] }
    notes_dict = {}

    for eleve in eleves:
        notes = Notes.objects.filter(
            eleve=eleve,
            matiere=matiere,
            periode=periode
        ).order_by('id')[:5]  # On prend max 5 notes par élève
        notes_dict[eleve.id] = list(notes)

        # Compléter avec des objets "vides" si moins de 5
        while len(notes_dict[eleve.id]) < 5:
            notes_dict[eleve.id].append(None)

    return render(request, 'frontoffice/notes/modifier_notes_classe.html', {
        'classe': classe,
        'matiere': matiere,
        'periode': periode,
        'eleves': eleves,
        'notes_dict': notes_dict,
        'types_evaluation': types_evaluation,
        'range_5': range(5),
    })
    
@fonctionnalite_autorisee('modifier_notes_classe')    
def modifier_notes_classe(request, classe_id, matiere_id, periode_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    matiere = get_object_or_404(Matieres, pk=matiere_id)
    periode = get_object_or_404(Periodes, pk=periode_id)

    eleves = Eleves.objects.filter(inscriptions__classe=classe).distinct()
    types_evaluation = TypeEvaluation.objects.all()
    notes_dict = {}

    for eleve in eleves:
        notes = Notes.objects.filter(
            eleve=eleve,
            matiere=matiere,
            periode=periode
        ).order_by('id')[:5]  # Récupère au max 5 notes
        notes = list(notes)

        # Remplir avec None si moins de 5
        while len(notes) < 5:
            notes.append(None)

        notes_dict[eleve.id] = notes

    return render(request, 'frontoffice/notes/modifier_notes_classe.html', {
        'classe': classe,
        'matiere': matiere,
        'periode': periode,
        'eleves': eleves,
        'notes_dict': notes_dict,
        'types_evaluation': types_evaluation,
        'range_5': range(5),
    })
