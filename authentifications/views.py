from django.shortcuts import render, redirect, get_object_or_404

from authentifications.decorators import fonctionnalite_autorisee
from authentifications.serializers import ClasseSerializer, EleveDetailSerializer, EleveInscritSerializer, EleveSerializer, EleveWriteSerializer, ModaliteCantinesSerializer, ModaliteTransportsSerializer, PaiementCantineSerializer, PaiementSerializer, PaiementTransportSerializer
from cores.models import AnneeScolaires
from eleves.models import Eleves, EvenementScolaire, Inscriptions, LienParente, Parents, Relances, Scolarites
from eleves.views import get_parent
from enseignants.models import Personnels
from etablissements.models import Classes, EmploiTemps, Etablissements
from notes.models import Notes
from scolarites.models import Echeances, ModaliteCantines, ModalitePaiements, ModaliteTransports, Paiements, PaiementsCantines, PaiementsTransports
from sms.models import NotificationSMS
from .models import HistoriqueConnexion, Roles, Utilisateurs, AccesFonctionnalites
from .forms import RoleForm, UtilisateurDirecForm, UtilisateurEconForm, UtilisateurForm, AccesFonctionnaliteForm, UtilisateurPareForm, UtilisateurPersForm, UtilisateurSecreForm, UtilisateurUpdateForm

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from datetime import date


def no_access(request):
    return render(request, 'errors/no_access.html')

def no_access_back(request):
    return render(request, 'errors/no_access_back.html')

@login_required
def historique_connexions(request): 
    #historique = HistoriqueConnexion.objects.filter(utilisateur=request.user).order_by('-date_heure')
    historique = HistoriqueConnexion.objects.all().order_by('-date_heure')
    return render(request, 'auth/historique.html', {'historique': historique})

# === AUTHENTIFICATION ===========================================================================================================================================================
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password,is_active=True)

        if user:
            login(request, user)
            role = user.role.nom if user.role else ''

            # Redirection selon le rôle
            if role in ['Secrétaire Exécutif', 'Comptabilité', 'Administrateur','Trésorerie']:
                return redirect('dashboard_tresorerie')
            elif role in ['Direction','Économat']:
                return redirect('dashboard_direction')
            #elif role == 'Économat':
            #    return redirect('dashboard_economat')
            #elif role == 'Enseignants':
            #    return redirect('dashboard_enseignant')
            elif role == 'Parents':
                return redirect('espace_parent')
            
            #elif role == 'Trésorerie':
            #    return redirect('dashboard_tresorerie')
            #elif role == 'Comptabilité':
            #    return redirect('dashboard_comptabilite')
            # elif role == 'Administrateur':
            #    return redirect('dashboard_administrateur')
            # else:
            #     return redirect('dashboard_general')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe invalide.", extra_tags='auth')
    
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def basculer_activation_utilisateur(request, user_id):
    utilisateur = get_object_or_404(Utilisateurs, pk=user_id)
    utilisateur.is_active = not utilisateur.is_active
    utilisateur.save()
    etat = "activé" if utilisateur.is_active else "désactivé"
    messages.success(request, f"L'utilisateur {utilisateur.username} a été {etat} avec succès.")
    return redirect('liste_utilisateurs')  # adapte selon ton nom d’URL
# ==============================================================================================================================================================

# === ROLES ===========================================================================================================================================================
def liste_roles(request):
    roles = Roles.objects.all()
    return render(request, 'backoffice/authentifications/roles/liste.html', {'roles': roles})

def creer_roleOK(request):
    form = RoleForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_roles')
    return render(request, 'backoffice/authentifications/roles/formulaire.html', {'form': form})

def creer_role(request):
    form = RoleForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_roles')
    return render(request, 'backoffice/authentifications/roles/formulaire.html', {'form': form})

def modifier_role(request, pk):
    role = get_object_or_404(Roles, pk=pk)
    form = RoleForm(request.POST or None, instance=role)
    if form.is_valid():
        form.save()
        return redirect('liste_roles')
    return render(request, 'backoffice/authentifications/roles/formulaire.html', {'form': form})

def supprimer_role(request, pk):
    role = get_object_or_404(Roles, pk=pk)
    if request.method == 'POST':
        role.delete()
        return redirect('liste_roles')
    return render(request, 'backoffice/authentifications/roles/confirm_suppression.html', {'objet': role}) 

def voir_acces_role(request, role_id):
    role = get_object_or_404(Roles, pk=role_id)
    acces = AccesFonctionnalites.objects.filter(role=role)
    return render(request, 'backoffice/authentifications/roles/acces.html', {'role': role, 'acces': acces})

def gestion_acces_role(request, role_id):
    role = get_object_or_404(Roles, pk=role_id)
    acces = AccesFonctionnalites.objects.filter(role=role).order_by('fonctionnalite')

    if request.method == 'POST':
        for acces_fonct in acces:
            checkbox_name = f'autorise_{acces_fonct.id}'
            autorise = checkbox_name in request.POST
            if acces_fonct.autorise != autorise:
                acces_fonct.autorise = autorise
                acces_fonct.save()

        return redirect('liste_roles')  # ou où tu veux rediriger

    return render(request, 'backoffice/authentifications/roles/gestion_acces_role.html', {
        'role': role,
        'acces': acces
    })

def gestion_acces_role_secretariat(request, role_id):
    role = get_object_or_404(Roles, pk=role_id)
    acces = AccesFonctionnalites.objects.filter(role=role).order_by('fonctionnalite')

    if request.method == 'POST':
        for acces_fonct in acces:
            checkbox_name = f'autorise_{acces_fonct.id}'
            autorise = checkbox_name in request.POST
            if acces_fonct.autorise != autorise:
                acces_fonct.autorise = autorise
                acces_fonct.save()

        return redirect('liste_roles')  # ou où tu veux rediriger

    return render(request, 'backoffice/authentifications/roles/gestion_acces_role.html', {
        'role': role,
        'acces': acces
    })

@fonctionnalite_autorisee('maj_acces_ajax')
def maj_acces_ajax(request):
    if request.method == 'POST':
        id_acces = request.POST.get('id')
        valeur = request.POST.get('autorise') == 'true'

        try:
            acces = AccesFonctionnalites.objects.get(pk=id_acces)
            acces.autorise = valeur
            acces.save()
            return JsonResponse({'success': True})
        except AccesFonctionnalites.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Accès introuvable'})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})
 
# === UTILISATEURS ======================================================================================================================================================
def liste_utilisateurs(request):
    utilisateurs = Utilisateurs.objects.all()
    return render(request, 'backoffice/authentifications/utilisateurs/liste.html', {'utilisateurs': utilisateurs})

from django.db.models import Q
@fonctionnalite_autorisee('liste_utilisateurs_secretariat')
def liste_utilisateurs_secretariat(request):
    utilisateurs = Utilisateurs.objects.filter(
        Q(role__nom='Secrétaire Exécutif') |
        Q(role__nom='Trésorerie') |
        Q(role__nom='Comptabilité')
    )
    return render(request, 'backoffice/authentifications/utilisateurs/liste_secretariat.html', {'utilisateurs': utilisateurs})

@fonctionnalite_autorisee('liste_utilisateurs_etablissement')
def liste_utilisateurs_etablissement(request):
    utilisateurs = Utilisateurs.objects.filter(role__nom='Direction')
    return render(request, 'backoffice/authentifications/utilisateurs/liste_direction.html', {'utilisateurs': utilisateurs})

@fonctionnalite_autorisee('liste_utilisateurs_economat')
def liste_utilisateurs_economat(request):
    utilisateurs = Utilisateurs.objects.filter(role__nom='Économat')
    return render(request, 'backoffice/authentifications/utilisateurs/liste_economat.html', {'utilisateurs': utilisateurs})

@fonctionnalite_autorisee('liste_utilisateurs_parent')
def liste_utilisateurs_parent(request):
    utilisateurs = Utilisateurs.objects.filter(role__nom='Parents')
    return render(request, 'backoffice/authentifications/utilisateurs/liste_parent.html', {'utilisateurs': utilisateurs})

@fonctionnalite_autorisee('liste_utilisateurs_personnel')
def liste_utilisateurs_personnel(request):
    utilisateurs = Utilisateurs.objects.filter(
        Q(role__nom='Enseignants') |
        Q(role__nom='Professeurs') 
    )
    return render(request, 'backoffice/authentifications/utilisateurs/liste_personnel.html', {'utilisateurs': utilisateurs})

def ajouter_utilisateur(request):
    form = UtilisateurForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('liste_utilisateurs')
    return render(request, 'backoffice/authentifications/utilisateurs/formulaire.html', {'form': form, 'titre': 'Ajouter un utilisateur'})

def modifier_utilisateur_pwd(request, pk):
    utilisateur = get_object_or_404(Utilisateurs, pk=pk)

    if request.method == 'POST':
        form = UtilisateurUpdateForm(request.POST, request.FILES, instance=utilisateur)
        if form.is_valid():
            form.save()
            return redirect('liste_utilisateurs')  # à adapter selon ta route
    else:
        form = UtilisateurUpdateForm(instance=utilisateur, initial={
            'actif': utilisateur.is_active
        })

    return render(request, 'backoffice/authentifications/utilisateurs/modifier_utilisateur.html', {
        'form': form,
        'utilisateur': utilisateur
    })


@fonctionnalite_autorisee('modifier_utilisateur')  
def modifier_utilisateur(request, pk): 
    utilisateur = get_object_or_404(Utilisateurs, pk=pk)
    form = UtilisateurForm(request.POST or None, request.FILES or None, instance=utilisateur)
    if form.is_valid():
        form.save()
        return redirect('liste_utilisateurs')
    return render(request, 'backoffice/authentifications/utilisateurs/formulaire.html', {'form': form, 'titre': 'Modifier l’utilisateur'})

@fonctionnalite_autorisee('modifier_utilisateur_secre')
def modifier_utilisateur_secre(request, pk): 
    utilisateur = get_object_or_404(Utilisateurs, pk=pk)
    form = UtilisateurSecreForm(request.POST or None, request.FILES or None, instance=utilisateur)
    if form.is_valid():
        form.save()
        return redirect('liste_utilisateurs_secretariat')
    return render(request, 'backoffice/authentifications/utilisateurs/formulaire.html', {'form': form, 'titre': 'Modifier l’utilisateur'})

@fonctionnalite_autorisee('modifier_utilisateur_econo')
def modifier_utilisateur_econo(request, pk): 
    utilisateur = get_object_or_404(Utilisateurs, pk=pk)
    form = UtilisateurEconForm(request.POST or None, request.FILES or None, instance=utilisateur)
    if form.is_valid():
        form.save()
        return redirect('liste_utilisateurs_economat')
    return render(request, 'backoffice/authentifications/utilisateurs/formulaire.html', {'form': form, 'titre': 'Modifier l’utilisateur'})

@fonctionnalite_autorisee('modifier_utilisateur_direc')
def modifier_utilisateur_direc(request, pk): 
    utilisateur = get_object_or_404(Utilisateurs, pk=pk)
    form = UtilisateurDirecForm(request.POST or None, request.FILES or None, instance=utilisateur)
    if form.is_valid():
        form.save()
        return redirect('liste_utilisateurs_etablissement')
    return render(request, 'backoffice/authentifications/utilisateurs/formulaire.html', {'form': form, 'titre': 'Modifier l’utilisateur'})

@fonctionnalite_autorisee('modifier_utilisateur_pers')
def modifier_utilisateur_pers(request, pk): 
    utilisateur = get_object_or_404(Utilisateurs, pk=pk)
    form = UtilisateurPersForm(request.POST or None, request.FILES or None, instance=utilisateur)
    if form.is_valid():
        form.save()
        return redirect('liste_utilisateurs_personnel')
    return render(request, 'backoffice/authentifications/utilisateurs/formulaire.html', {'form': form, 'titre': 'Modifier l’utilisateur'})

@fonctionnalite_autorisee('modifier_utilisateur_pare')
def modifier_utilisateur_pare(request, pk): 
    utilisateur = get_object_or_404(Utilisateurs, pk=pk)
    form = UtilisateurPareForm(request.POST or None, request.FILES or None, instance=utilisateur)
    if form.is_valid():
        form.save()
        return redirect('liste_utilisateurs_parent')
    return render(request, 'backoffice/authentifications/utilisateurs/formulaire.html', {'form': form, 'titre': 'Modifier l’utilisateur'})

def supprimer_utilisateur(request, pk):
    utilisateur = get_object_or_404(Utilisateurs, pk=pk)
    if request.method == 'POST':
        utilisateur.delete()
        return redirect('liste_utilisateurs')
    return render(request, 'backoffice/authentifications/utilisateurs/confirm_delete.html', {'utilisateur': utilisateur})


# === ACCES FONCTIONNALITÉS ================================================================================================================================================
def liste_acces(request):
    acces = AccesFonctionnalites.objects.all()
    return render(request, 'backoffice/authentifications/acces/liste.html', {'acces': acces})

@fonctionnalite_autorisee('liste_acces_secretariat')
def liste_acces_secretariat(request):
    acces = AccesFonctionnalites.objects.filter(role__nom__in=['Secrétaire Exécutif', 'Trésorerie', 'Comptabilité'])
    return render(request, 'backoffice/authentifications/acces/liste_service.html', {'acces': acces})

@fonctionnalite_autorisee('liste_acces_economat')
def liste_acces_economat(request):
    acces = AccesFonctionnalites.objects.filter(role__nom__in=['Économat'])
    return render(request, 'backoffice/authentifications/acces/liste_service.html', {'acces': acces})

@fonctionnalite_autorisee('liste_acces_etablissement')
def liste_acces_etablissement(request):
    acces = AccesFonctionnalites.objects.filter(role__nom__in=['Direction'])
    return render(request, 'backoffice/authentifications/acces/liste_service.html', {'acces': acces})

@fonctionnalite_autorisee('liste_acces_personnels')
def liste_acces_personnels(request):
    acces = AccesFonctionnalites.objects.filter(role__nom__in=['Professeurs', 'Enseignants'])
    return render(request, 'backoffice/authentifications/acces/liste_service.html', {'acces': acces})

@fonctionnalite_autorisee('liste_acces_parent')
def liste_acces_parent(request):
    acces = AccesFonctionnalites.objects.filter(role__nom__in=['Parents'])
    return render(request, 'backoffice/authentifications/acces/liste_service.html', {'acces': acces})

def creer_acces(request):
    form = AccesFonctionnaliteForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_acces')
    return render(request, 'backoffice/authentifications/acces/formulaire.html', {'form': form})

# === ACCES DASHBOARD ================================================================================================================================================
@login_required

def dashboard_tresorerie(request):
    annee_active = AnneeScolaires.objects.get(active=True)

    # Inscriptions filtrées pour l'établissement et l'année active
    inscriptions = Inscriptions.objects.filter(
        annee_scolaire=annee_active,
    )

    # Nombre total d'élèves inscrits
    total_inscrits = inscriptions.count()
    # Primaire
    cycle_filtre_primaire = ['Primaire','Préscolaire']
    total_inscrits_primaire = inscriptions.filter(
        classe__etablissement__types__nom__in=cycle_filtre_primaire
    ).distinct().count()
    # Secondaire (Collège, Lycée, Technique)
    cycle_filtre_secondaire = ['Collège', 'Lycée', 'Technique']
    total_inscrits_secondaire = inscriptions.filter(
        classe__etablissement__types__nom__in=cycle_filtre_secondaire
    ).distinct().count()


    # Nombre de garçons et de filles
    total_garcons = inscriptions.filter(eleve__sexe='M').count()
    total_filles = inscriptions.filter(eleve__sexe='F').count()
    # Primaire
    total_garcons_primaire = inscriptions.filter(eleve__sexe='M', classe__etablissement__types__nom__in=cycle_filtre_primaire).distinct().count()
    total_filles_primaire = inscriptions.filter(eleve__sexe='F', classe__etablissement__types__nom__in=cycle_filtre_primaire).distinct().count()
    # Secondaire (Collège, Lycée, Technique)
    total_garcons_secondaire = inscriptions.filter(eleve__sexe='M', classe__etablissement__types__nom__in=cycle_filtre_secondaire).distinct().count()
    total_filles_secondaire  = inscriptions.filter(eleve__sexe='F', classe__etablissement__types__nom__in=cycle_filtre_secondaire).distinct().count()

    # Nombre de classes avec au moins un élève inscrit
    classes_avec_inscrits = inscriptions.values('classe').distinct().count()
    # Primaire
    classes_avec_inscrits_primaire = inscriptions.filter(classe__etablissement__types__nom__in=cycle_filtre_primaire).values('classe').distinct().count()
    # Secondaire (Collège, Lycée, Technique)
    classes_avec_inscrits_secondaire = inscriptions.filter(classe__etablissement__types__nom__in=cycle_filtre_secondaire).values('classe').distinct().count()

    # Nombre total de places disponibles dans l'établissement
    total_places = Classes.objects.filter(annee_scolaire=annee_active).aggregate(total=Sum('capacite'))['total'] or 0
    # Primaire
    total_places_primaire = Classes.objects.filter(annee_scolaire=annee_active, etablissement__types__nom__in=cycle_filtre_primaire).distinct().aggregate(total=Sum('capacite'))['total'] or 0
    # Secondaire (Collège, Lycée, Technique)
    total_places_secondaire = Classes.objects.filter(annee_scolaire=annee_active, etablissement__types__nom__in=cycle_filtre_secondaire).distinct().aggregate(total=Sum('capacite'))['total'] or 0
    

    # Nombre total d'élèves déjà affectés dans les classes
    total_places_occupees = inscriptions.exclude(classe__isnull=True).count()

    # Places restantes
    places_restantes = max(0, total_places - total_places_occupees)
    
    # Taux d’occupation
    taux_occupation = round((total_inscrits / total_places) * 100, 2) if total_places > 0 else 0
    taux_restant = 100 - taux_occupation
    
    inscriptions_par_niveau = Inscriptions.objects.filter(
        annee_scolaire=annee_active
    ).values('classe__niveau__nom').annotate(total=Count('id')).order_by('classe__niveau__nom')

    labels_niveaux = [item['classe__niveau__nom'] for item in inscriptions_par_niveau]
    data_niveaux = [item['total'] for item in inscriptions_par_niveau]
    
    resultats = (
        Relances.objects
        .filter(inscription__annee_scolaire=annee_active)
        .values('inscription__classe__etablissement__nom')
        .annotate(
            total_echeance=Sum('echeance_montant'),
            total_verse=Sum('total_verse'),
            total_solde=Sum('total_solde')
        )
        .order_by('inscription__classe__etablissement__nom')
    )


    # 10 dernières inscriptions
    dernieres_inscriptions = inscriptions.select_related('eleve', 'classe__niveau').order_by('-date_inscription')[:10]
    
    today = date.today()

    # Filtrage des paiements validés pour aujourd'hui----------------------------------------------
    paiements = Paiements.objects.filter(
        date_paiement=today,
        statut_validation__in=['valide', 'partiel']
    ).select_related('inscription__classe__etablissement')

    # Regroupement par établissement
    paiements_par_etab = {}
    for paiement in paiements:
        etab = paiement.inscription.classe.etablissement
        if etab not in paiements_par_etab:
            paiements_par_etab[etab] = 0
        paiements_par_etab[etab] += paiement.montant
    print(paiements_par_etab.items())
    # Pour la courbe : préparation des données
    labels = [etab.nom for etab in paiements_par_etab.keys()]
    valeurs = [total for total in paiements_par_etab.values()]

    context = {
        'paiements_par_etab': paiements_par_etab.items(),
        'labels': labels,
        'valeurs': valeurs,
        'date': today,
  
        'annee_active': annee_active,
        'total_inscrits': total_inscrits,
        'total_garcons': total_garcons,
        'total_filles': total_filles,
        'classes_avec_inscrits': classes_avec_inscrits,
        'places_restantes': places_restantes,
        'dernieres_inscriptions': dernieres_inscriptions,
        #'chart_sexe': {
            'garcons': total_garcons,
            'filles': total_filles,
        #},
        'taux_occupation': taux_occupation,
        'taux_restant': taux_restant,
        'labels_niveaux': labels_niveaux,
        'data_niveaux': data_niveaux,
        
        'total_inscrits_secondaire' : total_inscrits_secondaire,
        'total_inscrits_primaire' : total_inscrits_primaire,
        'total_garcons_primaire' : total_garcons_primaire,
        'total_filles_primaire' : total_filles_primaire,
        'total_garcons_secondaire' : total_garcons_secondaire,
        'total_filles_secondaire' : total_filles_secondaire,
        'classes_avec_inscrits_primaire' : classes_avec_inscrits_primaire,
        'classes_avec_inscrits_secondaire' : classes_avec_inscrits_secondaire,
        'total_places_primaire' : total_places_primaire,
        'total_places_secondaire' : total_places_secondaire
    }

    return render(request, 'dashboard/dashboard_tresorerie.html', context)


from django.db.models import Count, Q,Sum

@fonctionnalite_autorisee('dashboard_direction')  
def dashboard_direction(request):
    etablissement = request.user.etablissement
    annee_active = AnneeScolaires.objects.get(active=True)

    # Inscriptions filtrées pour l'établissement et l'année active
    inscriptions = Inscriptions.objects.filter(
        annee_scolaire=annee_active,
        classe__etablissement=etablissement
    )

    # Nombre total d'élèves inscrits
    total_inscrits = inscriptions.count()

    # Nombre de garçons et de filles
    total_garcons = inscriptions.filter(eleve__sexe='M').count()
    total_filles = inscriptions.filter(eleve__sexe='F').count()

    # Nombre de classes avec au moins un élève inscrit
    classes_avec_inscrits = inscriptions.values('classe').distinct().count()

    # Nombre total de places disponibles dans l'établissement
    total_places = Classes.objects.filter(
        etablissement=etablissement,annee_scolaire=annee_active
    ).aggregate(
        total=Sum('capacite')
    )['total'] or 0

    # Nombre total d'élèves déjà affectés dans les classes
    total_places_occupees = inscriptions.exclude(classe__isnull=True).count()

    # Places restantes
    places_restantes = max(0, total_places - total_places_occupees)
    
    # Taux d’occupation
    taux_occupation = round((total_inscrits / total_places) * 100, 2) if total_places > 0 else 0
    taux_restant = 100 - taux_occupation
    
    inscriptions_par_niveau = Inscriptions.objects.filter(
        annee_scolaire=annee_active,
        classe__etablissement=etablissement
    ).values('classe__niveau__nom').annotate(total=Count('id')).order_by('classe__niveau__nom')

    labels_niveaux = [item['classe__niveau__nom'] for item in inscriptions_par_niveau]
    data_niveaux = [item['total'] for item in inscriptions_par_niveau]


    # 10 dernières inscriptions
    dernieres_inscriptions = inscriptions.select_related('eleve', 'classe__niveau').order_by('-date_inscription')[:10]

    context = {
        'annee_active': annee_active,
        'total_inscrits': total_inscrits,
        'total_garcons': total_garcons,
        'total_filles': total_filles,
        'classes_avec_inscrits': classes_avec_inscrits,
        'places_restantes': places_restantes,
        'dernieres_inscriptions': dernieres_inscriptions,
        #'chart_sexe': {
            'garcons': total_garcons,
            'filles': total_filles,
        #},
        'taux_occupation': taux_occupation,
        'taux_restant': taux_restant,
        'labels_niveaux': labels_niveaux,
        'data_niveaux': data_niveaux
    }

    return render(request, 'dashboard/dashboard_direction.html', context)

@fonctionnalite_autorisee('espace_parent')  
def espace_parent(request):
    parent = request.user.parents  # grâce au OneToOneField
    liens = LienParente.objects.filter(parent=parent).select_related('eleve')
    enfants = Eleves.objects.filter(parent=parent)

    return render(request, 'espace_parent/accueil.html', {
        'liens': liens,'enfants': enfants
    })

@fonctionnalite_autorisee('dashboard_parent')      
def dashboard_parent(request):
    parent = get_parent(request)
    enfants = Eleves.objects.filter(parent=parent)
    return render(request, 'parents/dashboard.html', {'enfants': enfants})


def dashboard_administrateur(request):
    annee_active = AnneeScolaires.objects.get(active=True)

    # Inscriptions filtrées pour l'établissement et l'année active
    inscriptions = Inscriptions.objects.filter(
        annee_scolaire=annee_active,
    )

    # Nombre total d'élèves inscrits
    total_inscrits = inscriptions.count()
    # Primaire
    cycle_filtre_primaire = ['Primaire','Préscolaire']
    total_inscrits_primaire = inscriptions.filter(
        classe__etablissement__types__nom__in=cycle_filtre_primaire
    ).distinct().count()
    # Secondaire (Collège, Lycée, Technique)
    cycle_filtre_secondaire = ['Collège', 'Lycée', 'Technique']
    total_inscrits_secondaire = inscriptions.filter(
        classe__etablissement__types__nom__in=cycle_filtre_secondaire
    ).distinct().count()


    # Nombre de garçons et de filles
    total_garcons = inscriptions.filter(eleve__sexe='M').count()
    total_filles = inscriptions.filter(eleve__sexe='F').count()
    # Primaire
    total_garcons_primaire = inscriptions.filter(eleve__sexe='M', classe__etablissement__types__nom__in=cycle_filtre_primaire).distinct().count()
    total_filles_primaire = inscriptions.filter(eleve__sexe='F', classe__etablissement__types__nom__in=cycle_filtre_primaire).distinct().count()
    # Secondaire (Collège, Lycée, Technique)
    total_garcons_secondaire = inscriptions.filter(eleve__sexe='M', classe__etablissement__types__nom__in=cycle_filtre_secondaire).distinct().count()
    total_filles_secondaire  = inscriptions.filter(eleve__sexe='F', classe__etablissement__types__nom__in=cycle_filtre_secondaire).distinct().count()

    # Nombre de classes avec au moins un élève inscrit
    classes_avec_inscrits = inscriptions.values('classe').distinct().count()
    # Primaire
    classes_avec_inscrits_primaire = inscriptions.filter(classe__etablissement__types__nom__in=cycle_filtre_primaire).values('classe').distinct().count()
    # Secondaire (Collège, Lycée, Technique)
    classes_avec_inscrits_secondaire = inscriptions.filter(classe__etablissement__types__nom__in=cycle_filtre_secondaire).values('classe').distinct().count()

    # Nombre total de places disponibles dans l'établissement
    total_places = Classes.objects.filter(annee_scolaire=annee_active).aggregate(total=Sum('capacite'))['total'] or 0
    # Primaire
    total_places_primaire = Classes.objects.filter(annee_scolaire=annee_active, etablissement__types__nom__in=cycle_filtre_primaire).distinct().aggregate(total=Sum('capacite'))['total'] or 0
    # Secondaire (Collège, Lycée, Technique)
    total_places_secondaire = Classes.objects.filter(annee_scolaire=annee_active, etablissement__types__nom__in=cycle_filtre_secondaire).distinct().aggregate(total=Sum('capacite'))['total'] or 0
    

    # Nombre total d'élèves déjà affectés dans les classes
    total_places_occupees = inscriptions.exclude(classe__isnull=True).count()

    # Places restantes
    places_restantes = max(0, total_places - total_places_occupees)
    
    # Taux d’occupation
    taux_occupation = round((total_inscrits / total_places) * 100, 2) if total_places > 0 else 0
    taux_restant = 100 - taux_occupation
    
    inscriptions_par_niveau = Inscriptions.objects.filter(
        annee_scolaire=annee_active
    ).values('classe__niveau__nom').annotate(total=Count('id')).order_by('classe__niveau__nom')

    labels_niveaux = [item['classe__niveau__nom'] for item in inscriptions_par_niveau]
    data_niveaux = [item['total'] for item in inscriptions_par_niveau]
    
    resultats = (
        Relances.objects
        .filter(inscription__annee_scolaire=annee_active)
        .values('inscription__classe__etablissement__nom')
        .annotate(
            total_echeance=Sum('echeance_montant'),
            total_verse=Sum('total_verse'),
            total_solde=Sum('total_solde')
        )
        .order_by('inscription__classe__etablissement__nom')
    )


    # 10 dernières inscriptions
    dernieres_inscriptions = inscriptions.select_related('eleve', 'classe__niveau').order_by('-date_inscription')[:10]
    
    today = date.today()

    # Filtrage des paiements validés pour aujourd'hui----------------------------------------------
    paiements = Paiements.objects.filter(
        date_paiement=today,
        statut_validation__in=['valide', 'partiel']
    ).select_related('inscription__classe__etablissement')

    # Regroupement par établissement
    paiements_par_etab = {}
    for paiement in paiements:
        etab = paiement.inscription.classe.etablissement
        if etab not in paiements_par_etab:
            paiements_par_etab[etab] = 0
        paiements_par_etab[etab] += paiement.montant
    print(paiements_par_etab.items())
    # Pour la courbe : préparation des données
    labels = [etab.nom for etab in paiements_par_etab.keys()]
    valeurs = [total for total in paiements_par_etab.values()]

    context = {
        'paiements_par_etab': paiements_par_etab.items(),
        'labels': labels,
        'valeurs': valeurs,
        'date': today,
  
        'annee_active': annee_active,
        'total_inscrits': total_inscrits,
        'total_garcons': total_garcons,
        'total_filles': total_filles,
        'classes_avec_inscrits': classes_avec_inscrits,
        'places_restantes': places_restantes,
        'dernieres_inscriptions': dernieres_inscriptions,
        #'chart_sexe': {
            'garcons': total_garcons,
            'filles': total_filles,
        #},
        'taux_occupation': taux_occupation,
        'taux_restant': taux_restant,
        'labels_niveaux': labels_niveaux,
        'data_niveaux': data_niveaux,
        
        'total_inscrits_secondaire' : total_inscrits_secondaire,
        'total_inscrits_primaire' : total_inscrits_primaire,
        'total_garcons_primaire' : total_garcons_primaire,
        'total_filles_primaire' : total_filles_primaire,
        'total_garcons_secondaire' : total_garcons_secondaire,
        'total_filles_secondaire' : total_filles_secondaire,
        'classes_avec_inscrits_primaire' : classes_avec_inscrits_primaire,
        'classes_avec_inscrits_secondaire' : classes_avec_inscrits_secondaire,
        'total_places_primaire' : total_places_primaire,
        'total_places_secondaire' : total_places_secondaire
    }

    return render(request, 'dashboard/dashboard_administrateur.html', context)

# API =======================================================================================================
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Mettre à jour la date de dernière connexion
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        # Générer ou récupérer le token
        token, created = self.get_token(user)

        # Se connecter (facultatif)
        login(request, user)

        # 👉 Assurez-vous de convertir `role` en string, peu importe le type
        return Response({
            'token': token.key,
            'role': str(getattr(user, 'role', '')),  # 👈 conversion explicite
            'last_login': user.last_login,
            'email': user.email,
            'user_id': user.pk,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            # 'photo': user.photo.url if user.photo else None,
        })

    def get_token(self, user):
        from rest_framework.authtoken.models import Token
        return Token.objects.get_or_create(user=user)
    
# Vue pour deconnection ==================================================================================================
@csrf_exempt
def logout_userbankBON(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@csrf_exempt
def logout_userbank(request):
    if request.method == 'POST':
        user = request.user if request.user.is_authenticated else None
        if user:
            logout(request)  # Ceci appellera le signal user_logged_out avec user correct
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

# Accueil parent ==========================================================================================================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Sum

class ParentDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        #msg = NotificationSMS.objects.all()
        # Récupérer le parent lié à l'utilisateur connecté
        parent = get_object_or_404(Parents, utilisateur=request.user)

        # Récupérer tous les élèves liés à ce parent via LienParente
        liens = LienParente.objects.filter(parent=parent).select_related('eleve')
        enfants = [lien.eleve for lien in liens]

        total_attendu = 0
        total_paye = 0

        for eleve in enfants:
            inscription = eleve.inscription_active()
            if inscription:
                total_attendu += inscription.montant_total_du()
                total_paye += inscription.montant_total_paye()

        solde = total_attendu - total_paye

        paiements_recents = [
            {
                "nom": p.inscription.eleve.nom,
                "prenom": p.inscription.eleve.prenoms,
                "classe": p.inscription.classe.nom if p.inscription.classe.nom else "",
            }
            for p in Paiements.objects.filter(inscription__eleve__in=enfants)
                                      .select_related('inscription__eleve')
                                      .order_by('-date_paiement')[:5]
        ]

        #messages_recents = [
        #    {
        #        "nom": msg.nom,
        #        "prenom": msg.prenoms,
        #        "classe": msg.get_classe_actuelle().nom if eleve.get_classe_actuelle() else "",
        #    }
        #    for eleve in enfants if eleve.messages.exists()
        #][:5]

        return Response({
            "total_attendu": total_attendu,
            "total_paye": total_paye,
            "solde": solde,
            "paiements_recents": paiements_recents,
            #"messages_recents": messages_recents,
        })

# liste des enfants ---------------------------------------------------------------------------------------------
class EnfantsDuParentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Récupère le parent connecté
        parent = get_object_or_404(Parents, utilisateur=request.user)

        # Récupère tous les enfants liés via LienParente
        liens = LienParente.objects.filter(parent=parent).select_related('eleve')

        enfants_data = []

        for lien in liens:
            enfant = lien.eleve
            inscription = enfant.inscription_active()

            if inscription and inscription.classe:
                enfants_data.append({
                    'id': enfant.id,
                    'nom': enfant.nom,
                    'prenom': enfant.prenoms,
                    'classe': inscription.classe.nom,
                    'niveau': inscription.classe.niveau.nom,
                    'etablissement': inscription.classe.etablissement.nom,
                    'matricule': enfant.matricule,
                    'lien': lien.lien
                })
            else:
                enfants_data.append({
                    'id': enfant.id,
                    'nom': enfant.nom,
                    'prenom': enfant.prenoms,
                    'classe': None,
                    'niveau': None,
                    'etablissement': None,
                    'matricule': enfant.matricule,
                    'lien': lien.lien
                })

        return Response(enfants_data)

# relances par enfants -------------------------------------------------------------------------------------------------
class RelancesEleveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, eleve_id):
        eleve = get_object_or_404(Eleves, pk=eleve_id)
        inscription = eleve.inscription_active()

        if not inscription:
            return Response([])

        relances = Relances.objects.filter(inscription=inscription, statut='active').order_by('-date_relance')
        data = [
            {
                'id': r.id,
                'echeance': r.echeance.nom,
                'echeance_id': r.echeance.id,
                'inscription_id': r.inscription.id,
                'date_relance': r.date_relance,
                'statut': r.statut,
                'montant': r.echeance_montant,
                'verse': r.total_verse,
                'solde': r.total_solde,
            }
            for r in relances
        ]
        #print(data)
        return Response(data)
    
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def modalites_cantine_non_payeesS(request, eleve_id):
    try:
        inscription = Inscriptions.objects.get(eleve_id=eleve_id, annee_scolaire__active=True, cantine=True)
    except Inscriptions.DoesNotExist:
        return Response([])

    # Récupère toutes les modalites pour l'établissement de l'inscription
    modalites = ModaliteCantines.objects.filter(
        etablissement=inscription.classe.etablissement,
        annee_scolaire=inscription.annee_scolaire,
    )

    # Filtre celles qui n'ont pas de paiement associé à cette inscription
    non_payees = modalites.exclude(
        id__in=PaiementsCantines.objects.filter(inscription=inscription).values_list('echeance_id', flat=True)
    )

    serializer = ModaliteCantinesSerializer(modalites, many=True)
    data = serializer.data

    # Injecte inscription_id dans chaque modalité
    for item in data:
        item['inscription_id'] = inscription.id

    return Response(data)
    #serializer = ModaliteCantinesSerializer(non_payees, many=True)
    #return Response(serializer.data)

@api_view(['GET'])
def modalites_transport_non_payeesS(request, eleve_id):
    try:
        inscription = Inscriptions.objects.get(eleve_id=eleve_id, annee_scolaire__active=True, cantine=True)
    except Inscriptions.DoesNotExist:
        return Response([])

    # Récupère toutes les modalites pour l'établissement de l'inscription
    modalites = ModaliteTransports.objects.filter(
        etablissement=inscription.classe.etablissement,
        annee_scolaire=inscription.annee_scolaire,
    )

    # Filtre celles qui n'ont pas de paiement associé à cette inscription
    non_payees = modalites.exclude(
        id__in=PaiementsTransports.objects.filter(inscription=inscription).values_list('echeance_id', flat=True)
    )

    serializer = ModaliteTransportsSerializer(modalites, many=True)
    data = serializer.data

    # Injecte inscription_id dans chaque modalité
    for item in data:
        item['inscription_id'] = inscription.id

    return Response(data)
    #serializer = ModaliteTransportsSerializer(non_payees, many=True)
    #return Response(serializer.data)
    
@api_view(['GET'])
def modalites_cantine_non_payees(request, eleve_id):
    try:
        inscription = Inscriptions.objects.get(eleve_id=eleve_id, annee_scolaire__active=True, cantine=True)
    except Inscriptions.DoesNotExist:
        return Response([])

    modalites = ModaliteCantines.objects.filter(
        etablissement=inscription.classe.etablissement,
        annee_scolaire=inscription.annee_scolaire,
    ).exclude(
        id__in=PaiementsCantines.objects.filter(inscription=inscription).values_list('echeance_id', flat=True)
    )

    serializer = ModaliteCantinesSerializer(modalites, many=True)
    data = serializer.data

    # Injecte inscription_id dans chaque modalité
    for item in data:
        item['inscription_id'] = inscription.id

    return Response(data)

@api_view(['GET'])
def modalites_transport_non_payees(request, eleve_id):
    try:
        inscription = Inscriptions.objects.get(eleve_id=eleve_id, annee_scolaire__active=True, transport=True)
    except Inscriptions.DoesNotExist:
        return Response([])

    modalites = ModaliteTransports.objects.filter(
        etablissement=inscription.classe.etablissement,
        annee_scolaire=inscription.annee_scolaire,
    ).exclude(
        id__in=PaiementsTransports.objects.filter(inscription=inscription).values_list('echeance_id', flat=True)
    )

    serializer = ModaliteTransportsSerializer(modalites, many=True)
    data = serializer.data

    # Injecte inscription_id dans chaque modalité
    for item in data:
        item['inscription_id'] = inscription.id

    return Response(data)

# liste des paiement scolarite - cantine - transport -------------------------------------------------------------------------------------------------

class PaiementsParTypeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        parent = get_object_or_404(Parents, utilisateur=request.user)
        liens = LienParente.objects.filter(parent=parent).select_related('eleve')
        annee_active = AnneeScolaires.objects.filter(active=True).first()

        data = {
            "scolarite": [],
            "cantine": [],
            "transport": [],
        }

        for lien in liens:
            eleve = lien.eleve
            inscription = eleve.inscription_active()

            # Paiements Scolarité
            paiements_sco = Paiements.objects.filter(inscription=inscription, inscription__annee_scolaire=annee_active)
            for p in paiements_sco:
                data["scolarite"].append({
                    "eleve": f"{eleve.prenoms} {eleve.nom}",
                    "montant": p.montant,
                    "date_paiement": p.date_paiement,
                    "mode": p.mode_paiement,
                })

            # Paiements Cantine
            paiements_cantine = PaiementsCantines.objects.filter(inscription=inscription, inscription__annee_scolaire__active=True)
            for p in paiements_cantine:
                data["cantine"].append({
                    "eleve": f"{eleve.prenoms} {eleve.nom}",
                    "montant": p.montant,
                    "date_paiement": p.date_paiement,
                    "mode": p.mode_paiement,
                })

            # Paiements Transport
            paiements_transport = PaiementsTransports.objects.filter(inscription=inscription, inscription__annee_scolaire__active=True)
            for p in paiements_transport:
                data["transport"].append({
                    "eleve": f"{eleve.prenoms} {eleve.nom}",
                    "montant": p.montant,
                    "date_paiement": p.date_paiement,
                    "mode": p.mode_paiement,
                })

        return Response(data)



class EvenementsParentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        parent = get_object_or_404(Parents, utilisateur=request.user)
        liens = LienParente.objects.filter(parent=parent).select_related('eleve')
        annee_active = AnneeScolaires.objects.filter(active=True).first()

        evenements = EvenementScolaire.objects.filter(
            eleve__in=[lien.eleve for lien in liens],
            annee_scolaire=annee_active
        ).select_related('eleve').order_by('-date_evenement')

        data = [
            {
                "eleve": f"{e.eleve.prenoms} {e.eleve.nom}",
                "type": e.type_evenement,
                "titre": e.titre,
                "description": e.description,
                "date_evenement": e.date_evenement.strftime('%Y-%m-%d'),
                "responsable": e.responsable,
            }
            for e in evenements
        ]

        return Response(data)
    
# fiche detail enfant pour le parent ----------------------------------------------------------------------------------------
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_fiche_enfants(request, id):
    eleve = get_object_or_404(Eleves, id=id)
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    
    inscriptions = Inscriptions.objects.filter(eleve=eleve).select_related('classe', 'annee_scolaire')
    inscription_active = inscriptions.filter(annee_scolaire=annee_active).first()
    
    parents = LienParente.objects.filter(eleve=eleve).select_related('parent__utilisateur')
    notes = Notes.objects.filter(eleve=eleve).select_related('matiere', 'periode')
    
    emplois = EmploiTemps.objects.filter(classe=inscription_active.classe).order_by('jour', 'heure_debut') if inscription_active else []

    return Response({
        'eleve': {
            'id': eleve.id,
            'nom': eleve.nom,
            'prenom': eleve.prenoms,
            'sexe': eleve.sexe,
            'date_naissance': eleve.date_naissance,
            'matricule': eleve.matricule,
        },
        'classe': {
            'id': inscription_active.classe.id,
            'nom': inscription_active.classe.nom,
        } if inscription_active else None,
        'inscriptions': [
            {
                'classe': i.classe.nom,
                'annee': i.annee_scolaire.libelle,
                'montant_total': i.montant_total_du(),
                'montant_paye': i.montant_total_paye(),
            } for i in inscriptions
        ],
        'parents': [
            {
                'nom': lp.parent.nom_complet,
                #'prenom': lp.parent.prenom,
                'lien': lp.lien,
                'email': lp.parent.utilisateur.email,
                'telephone': lp.parent.telephone,
            } for lp in parents
        ],
        'notes': [
            {
                'matiere': n.matiere.nom,
                'periode': n.periode.nom,
                'valeur': n.valeur,
            } for n in notes
        ],
        'emplois': [
            {
                'jour': e.jour,
                'heure_debut': e.heure_debut.strftime('%H:%M'),
                'heure_fin': e.heure_fin.strftime('%H:%M'),
                'matiere': e.matiere.nom,
                'professeur': e.professeur.nom_complet,
            } for e in emplois
        ],
    })


# Accueil direction ==========================================================================================================
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_direction_api(request):
    user = request.user
    etablissement = user.etablissement
    annee_active = AnneeScolaires.objects.get(active=True)

    inscriptions = Inscriptions.objects.filter(
        classe__etablissement=etablissement,
        annee_scolaire=annee_active
    ).select_related('eleve', 'classe')
    
    total_affecte = inscriptions.filter(statut='affecte').count()
    total_non_affecte = inscriptions.filter(statut='non_affecte').count()

    total_inscrits = inscriptions.count()
    total_garcons = inscriptions.filter(eleve__sexe='M').count()
    total_filles = inscriptions.filter(eleve__sexe='F').count()

    total_attendu = 0
    total_paye = 0

    for inscription in inscriptions:
        total_attendu += inscription.montant_total_du()
        total_paye += inscription.montant_total_paye()

    solde = total_attendu - total_paye

    paiements = Paiements.objects.filter(
        inscription__classe__etablissement=etablissement,
        inscription__annee_scolaire=annee_active,
        statut_validation__in=['valide', 'partiel']
    ).select_related('inscription__eleve', 'inscription__classe').order_by('-date_paiement')[:5]

    paiements_recents = []
    for p in paiements:
        paiements_recents.append({
            'nom': p.inscription.eleve.nom,
            'prenom': p.inscription.eleve.prenoms,
            'classe': str(p.inscription.classe.nom),
            'montant': p.montant,
            'date': p.date_paiement.strftime('%d/%m/%Y'),
        })

    return Response({
        'total_affecte': total_affecte,
        'total_non_affecte': total_non_affecte,
        'total_inscrits': total_inscrits,
        'total_garcons': total_garcons,
        'total_filles': total_filles,
        'total_attendu': float(total_attendu),
        'total_paye': float(total_paye),
        'solde': float(solde),
        'paiements_recents': paiements_recents,
    })

# liste eleves inscrit etablissement -----------------------------------------------------------------------------------

class ListeElevesDirectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        etablissement = request.user.etablissement
        try:
            annee_active = AnneeScolaires.objects.get(active=True)
        except AnneeScolaires.DoesNotExist:
            return Response({"error": "Aucune année scolaire active."}, status=400)

        inscriptions = Inscriptions.objects.filter(
            classe__etablissement=etablissement,
            annee_scolaire=annee_active
        ).select_related('eleve', 'classe')

        serializer = EleveInscritSerializer(inscriptions, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def eleve_par_matricule(request, matricule):
    try:
        eleve = Eleves.objects.get(matricule=matricule)
    except Eleves.DoesNotExist:
        return Response({'detail': 'Élève introuvable'}, status=404)

    annee_active = AnneeScolaires.objects.get(active=True)
    inscription = Inscriptions.objects.filter(eleve=eleve, annee_scolaire=annee_active).first()
    serializer = EleveDetailSerializer(eleve)
    
    data = serializer.data
    data['inscription_active'] = bool(inscription)

    return Response(data)


from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ajouter_eleve_api(request):
    data = request.data

    parent_data = data.get("parent", {})
    parent, _ = Parents.objects.get_or_create(
        telephone=parent_data.get("telephone"),
        defaults={
            "nom_complet": parent_data.get("nom_complet"),
            "email": parent_data.get("email"),
        }
    )

    eleve = Eleves.objects.create(
        matricule=data.get("matricule"),
        nom=data["nom"],
        prenoms=data["prenoms"],
        sexe=data["sexe"],
        date_naissance=data["date_naissance"],
        lieu_naissance=data.get("lieu_naissance"),
        nationalite=data.get("nationalite"),
        maladie_particuliere=data.get("maladie_particuliere"),
        parent=parent
    )

    serializer = EleveSerializer(eleve)
    #return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response({"message": "Élève ajouté avec succès"}, status=status.HTTP_201_CREATED)

# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class EleveViewSet(viewsets.ModelViewSet):
    queryset = Eleves.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EleveWriteSerializer
        return EleveSerializer

# afficher les classes pour inscription de l'api -------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_liste_classes_inscription(request):
    user = request.user
    if hasattr(user, 'etablissement'):
        classes = Classes.objects.filter(etablissement=user.etablissement)
    else:
        classes = Classes.objects.none()
    serializer = ClasseSerializer(classes, many=True)
    return Response(serializer.data)

# inscription des eleves depuis api -------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ajouter_inscription_api(request):
    data = request.data
    eleve_id = data.get('eleve_id')
    classe_id = data.get('classe_id')
    statut = data.get('statut')
    transport = data.get('transport')
    cantine = data.get('cantine')

    try:
        eleve = Eleves.objects.get(id=eleve_id)
        classe = Classes.objects.get(id=classe_id)
        annee = AnneeScolaires.objects.get(active=True)

        if Inscriptions.objects.filter(eleve=eleve, annee_scolaire=annee).exists():
            return Response({'detail': 'Élève déjà inscrit.'}, status=400)

        inscription = Inscriptions.objects.create(
            eleve=eleve,
            classe=classe,
            annee_scolaire=annee,
            statut=statut,
            utilisateur=request.user,
            cantine=cantine,
            transport=transport
        )
        
        # Déterminer la modalité à associer
        #statut = inscription.statut  # 'affecte' ou 'non_affecte'

        if statut == 'non_affecte':
            modalite = ModalitePaiements.objects.filter(
                etablissement=inscription.classe.etablissement if inscription.classe else request.user.etablissement,
                annee_scolaire=inscription.annee_scolaire,
                niveau=inscription.classe.niveau if inscription.classe else None,
                 applicable_aux_non_affectes=True
            ).first()
        else:  # statut == 'affecte'    
            modalite = ModalitePaiements.objects.filter(
                etablissement=inscription.classe.etablissement if inscription.classe else request.user.etablissement,
                annee_scolaire=inscription.annee_scolaire,
                niveau=inscription.classe.niveau if inscription.classe else None
            ).first()        

        # Sélection de la modalité de paiement
            #modalite = ModalitePaiements.objects.filter(
            #    etablissement=classe.etablissement,
            #    niveau=classe.niveau,
            #    annee_scolaire=annee,
            #    applicable_aux_non_affectes=(statut == 'non_affecte')
            #).first()

        if modalite:
            scolarite = Scolarites.objects.create(
                inscription=inscription,
                modalite=modalite
            )

            for echeance in Echeances.objects.filter(modalite=modalite):
                Relances.objects.create(
                    inscription=inscription,
                    echeance=echeance,
                    date_relance=echeance.date_limite,
                    statut='active',
                    echeance_montant=echeance.montant,
                    total_verse=0,
                    total_solde=echeance.montant
                )

        return Response({'id': inscription.id}, status=201)

    except Eleves.DoesNotExist:
        return Response({'detail': 'Élève introuvable.'}, status=404)
    except Classes.DoesNotExist:
        return Response({'detail': 'Classe introuvable.'}, status=404)
    except Exception as e:
        return Response({'detail': str(e)}, status=500)


# stat par classe etablissement api ------------------------------------------------------------------------------------------
from django.db.models import Count, Sum, Q

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_liste_classes(request):
    user = request.user
    if not hasattr(user, 'etablissement'):
        return Response([])

    annee_active = AnneeScolaires.objects.filter(active=True).first()
    if not annee_active:
        return Response([])

    # Récupération des classes de l’établissement
    classes = Classes.objects.filter(etablissement=user.etablissement)

    result = []
    for c in classes:
        # Récupération des inscriptions de l'année active pour la classe
        inscriptions = Inscriptions.objects.filter(classe=c, annee_scolaire=annee_active)
        nb_inscrits = inscriptions.count()
        if nb_inscrits == 0:
            continue  # on ignore les classes sans inscription

        garcons = inscriptions.filter(eleve__sexe='M').count()
        filles = inscriptions.filter(eleve__sexe='F').count()

        # Calcul manuel des totaux en Python
        scolarite_attendue = sum([ins.montant_total_du() for ins in inscriptions])
        scolarite_payee = sum([ins.montant_total_paye() for ins in inscriptions])
        solde = scolarite_attendue - scolarite_payee

        result.append({
            'nom': c.nom,
            'total': nb_inscrits,
            'garcons': garcons,
            'filles': filles,
            'attendu': scolarite_attendue,
            'paye': scolarite_payee,
            'solde': solde,
        })

    return Response(result)

# views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_direction_elevesoptiondeux(request):
    user = request.user
    if not hasattr(user, 'etablissement'):
        return Response([])

    annee_active = AnneeScolaires.objects.filter(active=True).first()
    if not annee_active:
        return Response([])

    inscriptions = Inscriptions.objects.select_related('eleve', 'classe')\
        .filter(
            annee_scolaire=annee_active,
            classe__etablissement=user.etablissement
        )

    eleves = []
    for ins in inscriptions:
        attendu = ins.montant_total or 0
        paye = ins.montant_paye or 0
        eleves.append({
            'id': ins.eleve.id,
            'nom': ins.eleve.nom,
            'prenom': ins.eleve.prenom,
            'classe': ins.classe.nom,
            'scolarite': attendu,
            'paye': paye,
            'solde': attendu - paye,
            'matricule': ins.eleve.matricule,
            'inscription_active': True,
        })

    return Response(eleves)

# liste des paiement scolarite - cantine - transport  directeur -------------------------------------------------------------------------------------------------
from rest_framework import status

class PaiementsParTypeDirectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        if not hasattr(user, 'etablissement'):
            return Response([], status=status.HTTP_400_BAD_REQUEST)

        annee_active = AnneeScolaires.objects.filter(active=True).first()
        if not annee_active:
            return Response([], status=status.HTTP_404_NOT_FOUND)

        data = {
            "scolarite": [],
            "cantine": [],
            "transport": [],
        }

        # Paiements Scolarité
        paiements_sco = Paiements.objects.filter(
            inscription__classe__etablissement=user.etablissement,
            inscription__annee_scolaire=annee_active
        )
        for p in paiements_sco:
            eleve = p.inscription.eleve
            data["scolarite"].append({
                "eleve": f"{eleve.prenoms} {eleve.nom}",
                "montant": p.montant,
                "date_paiement": p.date_paiement,
                "mode": p.mode_paiement,
            })

        # Paiements Cantine
        paiements_cantine = PaiementsCantines.objects.filter(
            inscription__classe__etablissement=user.etablissement,
            inscription__annee_scolaire=annee_active
        )
        for p in paiements_cantine:
            eleve = p.inscription.eleve
            data["cantine"].append({
                "eleve": f"{eleve.prenoms} {eleve.nom}",
                "montant": p.montant,
                "date_paiement": p.date_paiement,
                "mode": p.mode_paiement,
            })

        # Paiements Transport
        paiements_transport = PaiementsTransports.objects.filter(
            inscription__classe__etablissement=user.etablissement,
            inscription__annee_scolaire=annee_active
        )
        for p in paiements_transport:
            eleve = p.inscription.eleve
            data["transport"].append({
                "eleve": f"{eleve.prenoms} {eleve.nom}",
                "montant": p.montant,
                "date_paiement": p.date_paiement,
                "mode": p.mode_paiement,
            })

        return Response(data)

# paiement effectue par un directeur api ---------------------------------------------------------
from rest_framework import generics,viewsets

class PaiementCreateView(generics.CreateAPIView):
    queryset = Paiements.objects.all()
    serializer_class = PaiementSerializer

class PaiementViewSet(viewsets.ModelViewSet):
    queryset = Paiements.objects.all()
    serializer_class = PaiementSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}
    
class PaiementTransportViewSet(viewsets.ModelViewSet):
    queryset = PaiementsTransports.objects.all()
    serializer_class = PaiementTransportSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

class PaiementCantineViewSet(viewsets.ModelViewSet):
    queryset = PaiementsCantines.objects.all()
    serializer_class = PaiementCantineSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}    
    
# fiche detail eleve pour la direction ----------------------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_fiche_eleve(request, id):
    eleve = get_object_or_404(Eleves, id=id)
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    
    inscriptions = Inscriptions.objects.filter(eleve=eleve).select_related('classe', 'annee_scolaire')
    inscription_active = inscriptions.filter(annee_scolaire=annee_active).first()
    
    parents = LienParente.objects.filter(eleve=eleve).select_related('parent__utilisateur')
    notes = Notes.objects.filter(eleve=eleve).select_related('matiere', 'periode')
    
    emplois = EmploiTemps.objects.filter(classe=inscription_active.classe).order_by('jour', 'heure_debut') if inscription_active else []

    return Response({
        'eleve': {
            'id': eleve.id,
            'nom': eleve.nom,
            'prenom': eleve.prenoms,
            'sexe': eleve.sexe,
            'date_naissance': eleve.date_naissance,
            'matricule': eleve.matricule,
        },
        'classe': {
            'id': inscription_active.classe.id,
            'nom': inscription_active.classe.nom,
        } if inscription_active else None,
        'inscriptions': [
            {
                'classe': i.classe.nom,
                'annee': i.annee_scolaire.libelle,
                'montant_total': i.montant_total_du(),
                'montant_paye': i.montant_total_paye(),
            } for i in inscriptions
        ],
        'parents': [
            {
                'nom': lp.parent.nom_complet,
                #'prenom': lp.parent.prenom,
                'lien': lp.lien,
                'email': lp.parent.utilisateur.email,
                'telephone': lp.parent.telephone,
            } for lp in parents
        ],
        'notes': [
            {
                'matiere': n.matiere.nom,
                'periode': n.periode.nom,
                'valeur': n.valeur,
            } for n in notes
        ],
        'emplois': [
            {
                'jour': e.jour,
                'heure_debut': e.heure_debut.strftime('%H:%M'),
                'heure_fin': e.heure_fin.strftime('%H:%M'),
                'matiere': e.matiere.nom,
                'professeur': e.professeur.nom_complet,
            } for e in emplois
        ],
    })

# liste de mes enseignants direction -----------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_liste_enseignants(request):
    user = request.user
    if not hasattr(user, 'etablissement'):
        return Response([])

    enseignants = Personnels.objects.filter(
        etablissement=user.etablissement,
        actif=True  # filtre si tu as un champ "fonction"
    )

    data = []
    for e in enseignants:
        data.append({
            'id': e.id,
            'nom': e.nom_complet,
            'email': e.email,
            'telephone': e.telephone,
            'photo': e.photo.url if e.photo else None,
        })

    return Response(data)


# Accueil secretariat ==========================================================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_secretariat(request):
    # ✅ Année scolaire active
    annee_active = AnneeScolaires.objects.get(active=True)

    # ✅ Toutes les inscriptions de l'année active (tous établissements)
    inscriptions = Inscriptions.objects.filter(
        annee_scolaire=annee_active
    ).select_related('eleve', 'classe')

    total_affecte = inscriptions.filter(statut='affecte').count()
    total_non_affecte = inscriptions.filter(statut='non_affecte').count()

    total_inscrits = inscriptions.count()
    total_garcons = inscriptions.filter(eleve__sexe='M').count()
    total_filles = inscriptions.filter(eleve__sexe='F').count()

    total_attendu = 0
    total_paye = 0

    for inscription in inscriptions:
        total_attendu += inscription.montant_total_du()
        total_paye += inscription.montant_total_paye()

    solde = total_attendu - total_paye

    # ✅ Paiements valides de tous établissements, année active
    paiements = Paiements.objects.filter(
        inscription__annee_scolaire=annee_active,
        statut_validation__in=['valide', 'partiel']
    ).select_related('inscription__eleve', 'inscription__classe')\
     .order_by('-date_paiement')[:10]

    paiements_recents = []
    for p in paiements:
        paiements_recents.append({
            'nom': p.inscription.eleve.nom,
            'prenom': p.inscription.eleve.prenoms,
            'classe': str(p.inscription.classe),
            'montant': p.montant,
            'date': p.date_paiement.strftime('%d/%m/%Y'),
        })

    return Response({
        'total_affecte': total_affecte,
        'total_non_affecte': total_non_affecte,
        'total_inscrits': total_inscrits,
        'total_garcons': total_garcons,
        'total_filles': total_filles,
        'total_attendu': float(total_attendu),
        'total_paye': float(total_paye),
        'solde': float(solde),
        'paiements_recents': paiements_recents,
    })

# liste eleves inscrit secretariat -----------------------------------------------------------------------------------

# views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_eleves_secretariat(request):
    
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    if not annee_active:
        return Response([])

    inscriptions = Inscriptions.objects.filter(
        annee_scolaire=annee_active
    ).select_related('eleve', 'classe')

    data = []
    for ins in inscriptions:
        eleve = ins.eleve
        data.append({
            'id': eleve.id,
            'nom': eleve.nom,
            'prenom': eleve.prenoms,
            'sexe': eleve.sexe,
            'classe': ins.classe.nom,
            'etablissement': ins.classe.etablissement.nom,
            'scolarite': ins.montant_total_du(),
            'paye': ins.montant_total_paye(),
            'solde': ins.solde_restant(),
            'inscription_active': True,
        })

    return Response(data)

# stat par etablissement api ------------------------------------------------------------------------------------------
from django.db.models import Count, Sum, Q

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_liste_etablissements(request):
    
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    if not annee_active:
        return Response([])

    # Récupération des classes de l’établissement
    classes = Etablissements.objects.all()

    result = []
    for c in classes:
        # Récupération des inscriptions de l'année active pour la classe
        inscriptions = Inscriptions.objects.filter(classe__etablissement=c, annee_scolaire=annee_active)
        nb_inscrits = inscriptions.count()
        if nb_inscrits == 0:
            continue  # on ignore les classes sans inscription

        garcons = inscriptions.filter(eleve__sexe='M').count()
        filles = inscriptions.filter(eleve__sexe='F').count()

        # Calcul manuel des totaux en Python
        scolarite_attendue = sum([ins.montant_total_du() for ins in inscriptions])
        scolarite_payee = sum([ins.montant_total_paye() for ins in inscriptions])
        solde = scolarite_attendue - scolarite_payee

        result.append({
            'nom': c.nom,
            'total': nb_inscrits,
            'garcons': garcons,
            'filles': filles,
            'attendu': scolarite_attendue,
            'paye': scolarite_payee,
            'solde': solde,
        })

    return Response(result)

# liste des paiement scolarite - cantine - transport  Secretariat -------------------------------------------------------------------------------------------------
from rest_framework import status

class PaiementsParTypeSecretariatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        

        annee_active = AnneeScolaires.objects.filter(active=True).first()
        if not annee_active:
            return Response([], status=status.HTTP_404_NOT_FOUND)

        data = {
            "scolarite": [],
            "cantine": [],
            "transport": [],
        }

        # Paiements Scolarité
        paiements_sco = Paiements.objects.filter(
            inscription__annee_scolaire=annee_active
        )
        for p in paiements_sco:
            eleve = p.inscription.eleve
            data["scolarite"].append({
                "eleve": f"{eleve.prenoms} {eleve.nom}",
                "montant": p.montant,
                "date_paiement": p.date_paiement,
                "mode": p.mode_paiement,
            })

        # Paiements Cantine
        paiements_cantine = PaiementsCantines.objects.filter(
            inscription__annee_scolaire=annee_active
        )
        for p in paiements_cantine:
            eleve = p.inscription.eleve
            data["cantine"].append({
                "eleve": f"{eleve.prenoms} {eleve.nom}",
                "montant": p.montant,
                "date_paiement": p.date_paiement,
                "mode": p.mode_paiement,
            })

        # Paiements Transport
        paiements_transport = PaiementsTransports.objects.filter(
            inscription__annee_scolaire=annee_active
        )
        for p in paiements_transport:
            eleve = p.inscription.eleve
            data["transport"].append({
                "eleve": f"{eleve.prenoms} {eleve.nom}",
                "montant": p.montant,
                "date_paiement": p.date_paiement,
                "mode": p.mode_paiement,
            })

        return Response(data)
    
# liste de mes enseignants secretariat -----------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_liste_enseignants_secretariat(request):
   
    enseignants = Personnels.objects.filter(
        actif=True  # filtre si tu as un champ "fonction"
    )

    data = []
    for e in enseignants:
        data.append({
            'id': e.id,
            'nom': e.nom_complet,
            'email': e.email,
            'telephone': e.telephone,
            'photo': e.photo.url if e.photo else None,
        })

    return Response(data)

# retour apres paiement cinetpay-------------------------------------------------------------------------------------------------
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view
import json

@csrf_exempt
@api_view(['POST'])
def cinetpay_notify(request):
    """
    CinetPay va POSTER ici les données de confirmation.
    """
    data = json.loads(request.body.decode('utf-8'))
    transaction_id = data.get('transaction_id')
    status = data.get('status')
    amount = data.get('amount')

    # Tu peux logguer pour vérifier si CinetPay envoie bien les bonnes infos
    print("🟢 NOTIFICATION CINETPAY :", data)

    if status == 'ACCEPTED':
        # Chercher et valider le paiement
        try:
            paiement = Paiements.objects.get(transaction_id=transaction_id)
            paiement.statut = 'valide'
            paiement.date_validation = timezone.now()
            paiement.save()

            # Mettre à jour l'échéance associée
            echeance = paiement.echeance
            echeance.montant_paye += paiement.montant
            echeance.save()

            return JsonResponse({"message": "Paiement confirmé"}, status=200)
        except Paiements.DoesNotExist:
            return JsonResponse({"error": "Paiement introuvable"}, status=404)

    return JsonResponse({"message": "Statut non accepté"}, status=400)
