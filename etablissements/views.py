# views.py
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from authentifications.decorators import fonctionnalite_autorisee
from caisses.models import Caisses
from eleves.models import Inscriptions
from enseignants.models import Enseignants, Personnels
from matieres.models import Matieres
from .models import Etablissements, Niveaux, Classes, EmploiTemps, TypeEtablissement 
from .forms import ClasseEtForm, EmploiTempsPrimaireForm, EtablissementForm, NiveauForm, ClasseForm, EmploiTempsForm, TypeEtablissementForm

# === ÉTABLISSEMENTS ============================================================================================================================
def liste_etablissements(request):
    etablissements = Etablissements.objects.all()
    return render(request, 'backoffice/etablissements/etablissements/liste.html', {'etablissements': etablissements})

from django.shortcuts import render
from django.db.models import Count, Q
from .models import Etablissements, Cycles


def liste_typeetablissement(request):
    mois = TypeEtablissement.objects.all()
    return render(request, 'backoffice/etablissements/typeetablissements/liste.html', {'mois_list': mois})

def creer_typeetablissement(request):
    form = TypeEtablissementForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_typeetablissement')
    return render(request, 'backoffice/etablissements/typeetablissements/formulaire.html', {'form': form, 'titre': 'Créer un type etablissements'})

def modifier_typeetablissement(request, pk):
    mois = get_object_or_404(TypeEtablissement, pk=pk)
    form = TypeEtablissementForm(request.POST or None, instance=mois)
    if form.is_valid():
        form.save()
        return redirect('liste_typeetablissement')
    return render(request, 'backoffice/etablissements/typeetablissements/formulaire.html', {'form': form, 'titre': 'Modifier le type etablissements'})

def supprimer_typeetablissement(request, pk):
    mois = get_object_or_404(TypeEtablissement, pk=pk)
    if request.method == 'POST':
        mois.delete()
        return redirect('liste_typeetablissement')
    return render(request, 'backoffice/etablissements/typeetablissements/confirm_delete.html', {'objet': mois})

@fonctionnalite_autorisee('detail_etablissement')
def detail_etablissement(request, etablissement_id):
    etablissement = get_object_or_404(Etablissements, id=etablissement_id)
    annee_active = get_object_or_404(AnneeScolaires, active=True)

    inscriptions = Inscriptions.objects.filter(
        classe__etablissement=etablissement,
        annee_scolaire=annee_active
    )

    nb_eleves = inscriptions.count()
    nb_classes_avec_inscrits = inscriptions.values('classe').distinct().count()

    # Récupérer toutes les classes concernées avec leur nombre d'inscrits
    classes = (
        Classes.objects
        .filter(id__in=inscriptions.values_list('classe', flat=True))
        .annotate(nb_eleves=Count('inscriptions', filter=Q(inscriptions__annee_scolaire=annee_active)))
    )

    # enseignants = Enseignants.objects.filter(affectation__classe__etablissement=etablissement).distinct()
    enseignants = Personnels.objects.filter(etablissement=etablissement)

    return render(request, 'backoffice/etablissements/etablissements/detail_etablissement.html', {
        'etablissement': etablissement,
        'classes': classes,
        'enseignants': enseignants,
        'nb_eleves': nb_eleves,
        'nb_classes_avec_inscrits': nb_classes_avec_inscrits
    })






from django.core.paginator import Paginator
from django.db.models import Q, Count
@fonctionnalite_autorisee('etablissements_par_cycle')
def etablissements_par_cycle(request): 
    annee_active = get_object_or_404(AnneeScolaires, active=True)

    search_nom = request.GET.get('nom', '').strip()
    cycle_id = request.GET.get('cycle')

    etablissements = Etablissements.objects.annotate(
        nb_inscrits=Count(
            'classes__inscriptions__eleve',
            filter=Q(classes__inscriptions__annee_scolaire=annee_active),
            distinct=True
        )
    )

    if search_nom:
        etablissements = etablissements.filter(nom__icontains=search_nom)
    
    if cycle_id:
        etablissements = etablissements.filter(types__id=cycle_id)

    cycles = Cycles.objects.all()

    paginator = Paginator(etablissements, 8)  # 8 cartes par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'backoffice/etablissements/etablissements/etablissements_par_cycle.html', {
        'page_obj': page_obj,
        'cycles': cycles,
        'search_nom': search_nom,
        'selected_cycle': cycle_id,
    })
    
@fonctionnalite_autorisee('creer_etablissement')
def creer_etablissement(request):
    form = EtablissementForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        etablissement = form.save()
        # Récupération de l'année scolaire active
        annee_active = AnneeScolaires.objects.filter(active=True).first()
        if not annee_active:
            return redirect('liste_etablissements')

        # Création d'une caisse par défaut pour le nouvel établissement
        Caisses.objects.create(
            nom="Caisse Fonctionnement",
            etablissement=etablissement,
            annee_scolaire=annee_active,
            solde_initial=0
        )

        return redirect('liste_etablissements')
    return render(request, 'backoffice/etablissements/etablissements/formulaire.html', {'form': form})

@fonctionnalite_autorisee('modifier_etablissement')
def modifier_etablissement(request, pk):
    etab = get_object_or_404(Etablissements, pk=pk)
    form = EtablissementForm(request.POST or None, request.FILES or None, instance=etab)
    if form.is_valid():
        form.save()
        return redirect('liste_etablissements')
    return render(request, 'backoffice/etablissements/etablissements/formulaire.html', {'form': form})

@fonctionnalite_autorisee('supprimer_etablissement')
def supprimer_etablissement(request, pk):
    etab = get_object_or_404(Etablissements, pk=pk)
    etab.delete()
    return redirect('liste_etablissements')

# === NIVEAUX ============================================================================================================================================
def liste_niveaux(request):
    niveaux = Niveaux.objects.all()
    return render(request, 'backoffice/etablissements/niveaux/liste.html', {'niveaux': niveaux})

def creer_niveau(request):
    form = NiveauForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_niveaux')
    return render(request, 'backoffice/etablissements/niveaux/formulaire.html', {'form': form})

def modifier_niveau(request, pk):
    niveau = get_object_or_404(Niveaux, pk=pk)
    form = NiveauForm(request.POST or None, instance=niveau)
    if form.is_valid():
        form.save()
        return redirect('liste_niveaux')
    return render(request, 'backoffice/etablissements/niveaux/formulaire.html', {'form': form})

def supprimer_niveau(request, pk):
    niveau = get_object_or_404(Niveaux, pk=pk)
    niveau.delete()
    return redirect('liste_niveaux')

# === CLASSES =================================================================================================================================================
def liste_classes(request):
    classes = Classes.objects.all()
    return render(request, 'backoffice/etablissements/classes/liste.html', {'classes': classes})

from cores.models import AnneeScolaires

def creer_classe(request, etablissement_id=None):
    # récupérer l'année scolaire active
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    if not annee_active:
        return HttpResponse("Aucune année scolaire active définie.", status=400)

    if request.method == "POST":
        form = ClasseForm(request.POST)
        if form.is_valid():
            classe = form.save(commit=False)
            classe.annee_scolaire = annee_active
            if etablissement_id:
                classe.etablissement_id = etablissement_id
            classe.save()
            return redirect('liste_classes')
    else:
        initial_data = {'etablissement': etablissement_id} if etablissement_id else {}
        form = ClasseForm(initial=initial_data)

    return render(request, 'backoffice/etablissements/classes/formulaire.html', {'form': form})


def modifier_classe(request, pk):
    classe = get_object_or_404(Classes, pk=pk)
    form = ClasseForm(request.POST or None, instance=classe)
    if form.is_valid():
        form.save()
        return redirect('liste_classes')
    return render(request, 'backoffice/etablissements/classes/formulaire.html', {'form': form})

def supprimer_classe(request, pk):
    classe = get_object_or_404(Classes, pk=pk)
    classe.delete()
    return redirect('liste_classes')

# afficher les classes d’un établissement -------------------------------------------------------
def classes_etablissement(request, etablissement_id):
    etablissement = get_object_or_404(Etablissements, pk=etablissement_id)
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    classes = Classes.objects.filter(etablissement=etablissement, annee_scolaire=annee_active).order_by('niveau', 'nom')  # ou 'niveau__nom' si tu n’as pas de champ 'ordre'

    context = {
        'etablissement': etablissement,
        'annee_active': annee_active,
        'classes': classes
    }
    return render(request, 'backoffice/etablissements/etablissements/liste_par_etablissement.html', context)

@fonctionnalite_autorisee('creer_classe_etablissement') 
def creer_classe_etablissement(request, etablissement_id=None):
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    etablissement = request.user.etablissement

    if not annee_active:
        return HttpResponse("Aucune année scolaire active définie.", status=400)

    if request.method == "POST":
        form = ClasseEtForm(request.POST, etablissement=etablissement)
        if form.is_valid():
            classe = form.save(commit=False)
            classe.annee_scolaire = annee_active
            classe.etablissement = etablissement  # forcer l’établissement
            classe.save()
            return redirect('classes_avec_inscrits')
    else:
        form = ClasseEtForm(etablissement=etablissement) 

    return render(request, 'frontoffice/classes/formulaire_classe.html', {'form': form})


@fonctionnalite_autorisee('modifier_classe_etablissement') 
def modifier_classe_etablissement(request, pk):
    classe = get_object_or_404(Classes, pk=pk)
    form = ClasseEtForm(request.POST or None, instance=classe)
    if form.is_valid():
        form.save()
        return redirect('liste_classes')
    return render(request, 'frontoffice/classes/formulaire_classe.html', {'form': form})

# === EMPLOI DU TEMPS ================================================================================================================================
def liste_emploi(request):
    emplois = EmploiTemps.objects.all()
    return render(request, 'backoffice/etablissements/emplois/liste.html', {'emplois': emplois})

from django.http import JsonResponse

def get_professeurs_par_matiere(request):
    matiere_id = request.GET.get('matiere_id')
    if matiere_id:
        try:
            matiere = Matieres.objects.get(pk=matiere_id)
            profs = Enseignants.objects.filter(specialite__icontains=matiere.nom)
            data = [{'id': p.id, 'nom': p.nom_complet} for p in profs]
            return JsonResponse({'professeurs': data})
        except Matieres.DoesNotExist:
            return JsonResponse({'professeurs': []})
    return JsonResponse({'professeurs': []})

def creer_emploi_tempsf(request, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)

    if request.method == 'POST':
        form = EmploiTempsForm(request.POST, initial={'classe': classe})
        if form.is_valid():
            emploi = form.save(commit=False)
            emploi.classe = classe  # Forcer la classe
            emploi.save()
            return redirect('liste_classes')  # Redirection après enregistrement
    else:
        # 👇 Cette ligne est essentielle pour éviter l’erreur si la méthode n’est pas POST
        form = EmploiTempsForm(initial={'classe': classe})

    return render(request, 'frontoffice/classes/formulaire.html', {
        'form': form,
        'classe': classe,
    })

@fonctionnalite_autorisee('creer_emploi_temps')
def creer_emploi_temps(request, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)

    if request.method == 'POST':
        form = EmploiTempsForm(request.POST, initial={'classe': classe})
        if form.is_valid():
            emploi = form.save(commit=False)
            emploi.classe = classe  # Forcer la classe
            # 👉 Vérifie s’il y a un chevauchement avant de sauvegarder
            if emploi.chevauchement():
                form.add_error(None, "Un cours existe déjà à ce créneau pour cette classe.")
            else:
                emploi.save()
                return redirect('calendrier_emploi_classe', classe_id=classe.id)
    else:
        form = EmploiTempsForm(initial={'classe': classe})

    return render(request, 'frontoffice/classes/formulaire.html', {
        'form': form,
        'classe': classe,
    })

@fonctionnalite_autorisee('creer_emploi_temps_primaire')
def creer_emploi_temps_primaire(request, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    
    if request.method == 'POST':
        form = EmploiTempsPrimaireForm(request.POST, initial={'classe': classe})
        if form.is_valid():
            emploi = form.save(commit=False)
            emploi.classe = classe  # On force la classe liée 
            # 👉 Vérifie s’il y a un chevauchement avant de sauvegarder
            if emploi.chevauchement():
                form.add_error(None, "Un cours existe déjà à ce créneau pour cette classe.")
            else:
                emploi.save()
                return redirect('calendrier_emploi_classe', classe_id=classe.id)
    else:
        form = EmploiTempsPrimaireForm(initial={'classe': classe})
    
    return render(request, 'frontoffice/classes/formulaire_primaire.html', {
        'form': form,
        'classe': classe,
    })

@fonctionnalite_autorisee('calendrier_emploi_classe')
def calendrier_emploi_classe(request, classe_id):
    classe = get_object_or_404(Classes, id=classe_id)
    emplois = EmploiTemps.objects.filter(classe=classe).order_by('jour', 'heure_debut')

    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
    
    # Construire toutes les heures de début possibles
    heures = sorted(set(emploi.heure_debut.strftime('%H:%M') for emploi in emplois))
    heuresf = sorted(set(emploi.heure_fin.strftime('%H:%M') for emploi in emplois))

    #print(emplois) 
    #print(jours)
    #print(heures)
    # Afficher les matières et les professeurs pour chaque emploi
    #for emploi in emplois:
    #    print(f"Matière: {emploi.matiere.nom}")
         #print(f"Professeur: {emploi.professeur.nom_complet}")
        
    classe = Classes.objects.get(id=classe_id)
    etablissement = classe.etablissement
    types_etablissement = etablissement.types.all()  # ManyToMany vers Cycles

    # Exemple pour afficher les noms des types
    for cycle in types_etablissement:
        print(cycle.nom)
    
    #return render(request, 'frontoffice/classes/calendrier.html', {
    #    'classe': classe,
    #    'emplois': emplois,
    #    'jours': jours,
    #    'heures': heures,
    #    'heuresf': heuresf,
    #    'cycle' : cycle
    #})
    for cycle in types_etablissement:
        if cycle.nom == "Préscolaire" or cycle.nom == "Primaire":
            return render(request, 'frontoffice/classes/calendrier_primaire.html', {
                'classe': classe,
                'emplois': emplois,
                'jours': jours,
                'heures': heures,
                'heuresf': heuresf,
                'cycle': cycle
            })

    # Si aucun cycle n'est "Prescolaire et Primaire", on affiche le template par défaut
    return render(request, 'frontoffice/classes/calendrier.html', {
        'classe': classe,
        'emplois': emplois,
        'jours': jours,
        'heures': heures,
        'heuresf': heuresf,
        'cycle': cycle  # ou cycle par défaut si besoin
    })
    
   
@fonctionnalite_autorisee('modifier_emploi')
def modifier_emploiBon(request, pk):
    emploi = get_object_or_404(EmploiTemps, pk=pk)
    form = EmploiTempsForm(request.POST or None, instance=emploi)
    if form.is_valid():
        form.save()
        return redirect('calendrier_emploi_classe', classe_id=emploi.classe.id)
    return render(request, 'frontoffice/classes/formulaire.html', {'form': form})

@fonctionnalite_autorisee('modifier_emploi')
def modifier_emploi(request, pk):
    emploi = get_object_or_404(EmploiTemps, pk=pk)
    classe = emploi.classe  # On récupère la classe liée à cet emploi
    form = EmploiTempsForm(request.POST or None, instance=emploi)

    if form.is_valid():
        emploi_modifie = form.save(commit=False)
        emploi_modifie.classe = classe

        # Vérifie les chevauchements (en excluant l'emploi actuel de la comparaison)
        if emploi_modifie.chevauchement(exclure_id=emploi.id):
            form.add_error(None, "Un cours existe déjà à ce créneau pour cette classe.")
        else:
            emploi_modifie.save()
            return redirect('calendrier_emploi_classe', classe_id=classe.id)

    return render(request, 'frontoffice/classes/formulaire.html', {
        'form': form,
        'classe': classe,
    })



@fonctionnalite_autorisee('creer_emploi_temps_primaire')
def modifier_emploi_primaire(request, pk):
    emploi = get_object_or_404(EmploiTemps, pk=pk)
    classe = emploi.classe  # On récupère la classe liée à cet emploi
    form = EmploiTempsPrimaireForm(request.POST or None, instance=emploi)

    if form.is_valid():
        emploi_modifie = form.save(commit=False)
        emploi_modifie.classe = classe

        # Vérifie les chevauchements (en excluant l'emploi actuel de la comparaison)
        if emploi_modifie.chevauchement(exclure_id=emploi.id):
            form.add_error(None, "Un cours existe déjà à ce créneau pour cette classe.")
        else:
            emploi_modifie.save()
            return redirect('calendrier_emploi_classe', classe_id=classe.id)

    return render(request, 'frontoffice/classes/formulaire_primaire.html', {
        'form': form,
        'classe': classe,
    })


@fonctionnalite_autorisee('supprimer_emploi')
def supprimer_emploi(request, pk):
    emploi = get_object_or_404(EmploiTemps, pk=pk)
    emploi.delete()
    return redirect('calendrier_emploi_classe', classe_id=emploi.classe.id)


from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML

def emploi_temps_etablissement_pdf(request, etablissement_id):
    etablissement = get_object_or_404(Etablissements, pk=etablissement_id)
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    classes = Classes.objects.filter(etablissement=etablissement,annee_scolaire=annee_active)
    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']

    emplois_par_classe = {}
    heures_possibles = set()

    for classe in classes:
        emplois = EmploiTemps.objects.filter(classe=classe).order_by('jour', 'heure_debut')
        emplois_par_classe[classe] = emplois
        heures_possibles.update(emploi.heure_debut.strftime('%H:%M') for emploi in emplois)

    heures = sorted(heures_possibles)
    
    print(emplois_par_classe)
    print(heures)
    print(classes)

    template = get_template('frontoffice/classes/emplois_etablissement_pdf.html')
    html_string = template.render({
        'etablissement': etablissement,
        'annee': annee_active,
        'classes': classes,
        'emplois_par_classe': emplois_par_classe,
        'jours': jours,
        'heures': heures,
    })

    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    #response['Content-Disposition'] = f'filename="emplois_{etablissement.nom}.pdf"'
    response['Content-Disposition'] = f'attachment; filename="emploi_temps_emplois_{etablissement.nom}_{annee_active.libelle}.pdf"'
    return response


def emploi_temps_pdf(request, classe_id):
    classe = get_object_or_404(Classes, id=classe_id)
    etablissement = get_object_or_404(Etablissements, id=classe.etablissement_id)
    annee_active = AnneeScolaires.objects.filter(active=True).first()

    emplois = EmploiTemps.objects.filter(classe=classe).order_by('jour', 'heure_debut')
    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
    heures = sorted(set(emploi.heure_debut.strftime('%H:%M') for emploi in emplois))

    template = get_template('frontoffice/classes/emploi_pdf.html')
    html_string = template.render({
        'classe': classe,
        'etablissement': etablissement,
        'annee': annee_active,
        'emplois': emplois,
        'jours': jours,
        'heures': heures,
    })
    print(emplois)
    
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    #response['Content-Disposition'] = f'filename="emploi_temps_{classe.nom}.pdf"'
    response['Content-Disposition'] = f'attachment; filename="emploi_temps_{classe.nom}_{annee_active.libelle}.pdf"'
    return response


def creer_emploi_temps_back(request, classe_id):
    classe = get_object_or_404(Classes, pk=classe_id)
    form = EmploiTempsForm(request.POST or None, initial={'classe': classe})

    if request.method == 'POST':
        if form.is_valid():
            emploi = form.save(commit=False)
            emploi.classe = classe  # Forcer la classe
            emploi.save()
            return redirect('liste_classes')  # Ou autre redirection pertinente

    return render(request, 'backoffice/etablissements/emplois/formulaire.html', {
        'form': form,
        'classe': classe,
    })
    
def modifier_emploi_back(request, pk):
    emploi = get_object_or_404(EmploiTemps, pk=pk)
    form = EmploiTempsForm(request.POST or None, instance=emploi)
    if form.is_valid():
        form.save()
        return redirect('liste_emploi')
    return render(request, 'backoffice/etablissements/emplois/formulaire.html', {'form': form})

def supprimer_emploi_back(request, pk):
    emploi = get_object_or_404(EmploiTemps, pk=pk)
    emploi.delete()
    return redirect('liste_emploi')

#  backoffice pour -------------------------------------------------------------------------------
def calendrier_emploi_classe_back(request, classe_id):
    classe = get_object_or_404(Classes, id=classe_id)
    emplois = EmploiTemps.objects.filter(classe=classe).order_by('jour', 'heure_debut')

    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
    
    # Construire toutes les heures de début possibles
    heures = sorted(set(emploi.heure_debut.strftime('%H:%M') for emploi in emplois))

    return render(request, 'backoffice/etablissements/emplois/calendrier.html', {
        'classe': classe,
        'emplois': emplois,
        'jours': jours,
        'heures': heures,
    })
    
    
    
    
    
    
    
    









# ============================================================================ TEST BON ===========================================================================   
# ============================================================================ TEST BON =========================================================================== 
# ============================================================================ TEST BON =========================================================================== 
# ============================================================================ TEST BON =========================================================================== 
def etablissements_par_cycleBON(request): 
    annee_active = get_object_or_404(AnneeScolaires, active=True)
    etablissements = Etablissements.objects.annotate(
        nb_inscrits=Count(
            'classes__inscriptions__eleve',
            filter=Q(classes__inscriptions__annee_scolaire=annee_active),
            distinct=True
        )
    )

    print(etablissements)
    return render(request, 'backoffice/etablissements/etablissements/etablissements_par_cycle.html', {
        'etablissements': etablissements
    })
    
    
# ============================================================================ TEST BON =========================================================================== 
# ============================================================================ TEST BON =========================================================================== 
# ============================================================================ TEST BON =========================================================================== 