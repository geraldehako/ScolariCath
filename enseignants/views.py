from django.shortcuts import render, get_object_or_404, redirect

from authentifications.decorators import fonctionnalite_autorisee
from cores.models import AnneeScolaires
from enseignants.forms import AffectationForm, MutationPersonnelForm, PersonnelAdjoiForm, PersonnelDirecForm, PersonnelEconForm, PersonnelEtForm, PersonnelForm, PersonnelProfForm, PersonnelSecreForm, PosteForm, TenueDeClasseForm
from etablissements.models import Niveaux
from .models import Enseignants, Postes, Personnels, MutationPersonnel, TenueDeClasse, Affectation
from authentifications.models import Utilisateurs, Roles  # Si nécessaire
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from twilio.rest import Client
import secrets
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import xlwt
from django.http import HttpResponse

# Exemple pour Postes (à reproduire pour chaque modèle en changeant le nom)
def liste_postes(request):
    postes = Postes.objects.all()
    return render(request, 'backoffice/enseignants/postes/liste.html', {'postes': postes})

def creer_poste(request):
    form = PosteForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_postes')
    return render(request, 'backoffice/enseignants/postes/form.html', {'form': form})

def modifier_poste(request, pk):
    poste = get_object_or_404(Postes, pk=pk)
    form = PosteForm(request.POST or None, instance=poste)
    if form.is_valid():
        form.save()
        return redirect('liste_postes')
    return render(request, 'backoffice/enseignants/postes/form.html', {'form': form})


def supprimer_poste(request, pk):
    poste = get_object_or_404(Postes, pk=pk)
    poste.delete()
    return redirect('liste_postes')

def supprimer_posteBon(request, pk):
    poste = get_object_or_404(Postes, pk=pk)
    if request.method == 'POST':
        poste.delete()
        return redirect('liste_postes')
    return render(request, 'backoffice/enseignants/postes/confirm_delete.html', {'objet': poste})

# === PERSONNELS ===================================================================================================================

# liste des ensignants par etablissement ---------------------------------------------------------------
def liste_enseignantsT(request):
    enseignants = Personnels.objects.filter(etablissement=request.user.etablissement, actif=True)

    return render(request, 'frontoffice/personnels/liste_enseignants.html', {
        'enseignants': enseignants
    })
    
def liste_enseignantsTT(request):
    enseignants = Personnels.objects.filter(etablissement=request.user.etablissement)
    formulaires_tenue = {}
    for enseignant in enseignants:
        form = TenueDeClasseForm(user=request.user)
        formulaires_tenue[enseignant.id] = form

    return render(request, 'frontoffice/personnels/liste_enseignants.html', {
        'enseignants': enseignants,
        'formulaires_tenue': formulaires_tenue,
    })    
    
def liste_enseignantsTTT(request):
    enseignants = Personnels.objects.filter(etablissement=request.user.etablissement)
    formulaires_html = {}
    for enseignant in enseignants:
        form = TenueDeClasseForm(user=request.user)
        formulaires_html[enseignant.id] = form.as_p()  # Ici on prépare déjà le rendu HTML

    return render(request, 'frontoffice/personnels/liste_enseignants.html', {
        'enseignants': enseignants,
        'formulaires_html': formulaires_html,
    })

@fonctionnalite_autorisee('liste_enseignants')  
def liste_enseignants(request):
    enseignants = Personnels.objects.filter(etablissement=request.user.etablissement)
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    formulaires_html = {}
    # Dictionnaire des classes par enseignant
    classes_par_enseignant = {}
    for enseignant in enseignants:
        tenues = TenueDeClasse.objects.filter(enseignant=enseignant, annee_scolaire=annee_active)
        classes = [tenue.classe.nom for tenue in tenues]
        classes_par_enseignant[enseignant.id] = ", ".join(classes)
        form = TenueDeClasseForm(user=request.user)
        formulaires_html[enseignant.id] = form.as_p()  # Ici on prépare déjà le rendu HTML

    return render(request, 'frontoffice/personnels/liste_enseignants.html', {
        'enseignants': enseignants,
        'classes_par_enseignant': classes_par_enseignant,
        'formulaires_html': formulaires_html,
    })


def creer_personnel_etablissement(request):
    form = PersonnelEtForm(request.POST or None, request.FILES or None)
    etablissement = request.user.etablissement
    cycles = etablissement.types.all()
    noms_cycles = [cycle.nom for cycle in cycles]

    if any(nom in ['Préscolaire', 'Primaire'] for nom in noms_cycles):
        role = Roles.objects.get_or_create(nom="Enseignants")[0]
        poste = Postes.objects.get_or_create(nom="Enseignant")[0]
    elif any(nom in ['Collège', 'Lycée', 'Technique'] for nom in noms_cycles):
        role = Roles.objects.get_or_create(nom="Professeurs")[0]
        poste = Postes.objects.get_or_create(nom="Professeur")[0]

        
    if form.is_valid():
        personnel = form.save(commit=False)

        # Création automatique de l'utilisateur
        
        telephone = form.cleaned_data['telephone']
        email = form.cleaned_data['email']
        nom_complet = form.cleaned_data['nom_complet'].split()
        prenom = nom_complet[0]
        nom = " ".join(nom_complet[1:]) if len(nom_complet) > 1 else ''

        # Exemple : rôle par défaut "Personnel"
        #role_defaut = Roles.objects.get(nom="Personnel")

        utilisateur = Utilisateurs.objects.create(
            username=telephone,
            first_name=prenom,
            last_name=nom,
            etablissement=etablissement,
            photo=form.cleaned_data['photo'],
            role=role,
            email=email,
            telephone=telephone,
            password=make_password(telephone)  # Ou générer aléatoirement et envoyer par SMS/email
        )
        # Création du personnel
        personnel = form.save(commit=False)
        personnel.utilisateur = utilisateur
        personnel.etablissement = etablissement
        personnel.role = role
        personnel.poste = poste
        personnel.save()

        # Envoi email ou SMS (facultatif)
        # ... après création de l'utilisateur ......................................................................
        #mot_de_passe = "MotDePasse123"  # ou mot de passe généré
        #send_mail(
        #    subject="Votre compte utilisateur a été créé",
        #    message=f"Bonjour {utilisateur.first_name},\n\nVotre compte a été créé.\nIdentifiant : {utilisateur.username}\nMot de passe : {mot_de_passe}\n\nMerci.",
        #    from_email=None,
        #    recipient_list=[utilisateur.email],  # Assurez-vous que le champ email est renseigné
        #    fail_silently=False,
        #)
        
        # ENVOI DE SMS (via une API comme Twilio) ..........................................................................
        #message = f"Bienvenue {utilisateur.first_name}, identifiant: {utilisateur.username}, mot de passe: {mot_de_passe}"
        #envoyer_sms(utilisateur.telephone, message)

        return redirect('liste_enseignants')
    
    return render(request, 'frontoffice/personnels/form.html', {'form': form})


@fonctionnalite_autorisee('ajouter_tenue_de_classe')   
def ajouter_tenue_de_classe(request, enseignant_id):
    enseignant = Personnels.objects.get(pk=enseignant_id)
    annee_active = AnneeScolaires.objects.filter(active=True).first()

    if request.method == 'POST':
        form = TenueDeClasseForm(request.POST, user=request.user)
        if form.is_valid():
            tenue = form.save(commit=False)
            tenue.enseignant = enseignant
            tenue.annee_scolaire = annee_active
            tenue.save()
            return redirect('liste_enseignants')  # Redirige vers la page des enseignants
    else:
        form = TenueDeClasseForm(user=request.user)

    return render(request, 'frontoffice/enseignants/modal_tenue_de_classe.html', {
        'form': form,
        'enseignant': enseignant,
    })


def creer_personnell(request):
    if request.method == 'POST':
        form = PersonnelForm(request.POST, request.FILES)
        if form.is_valid():
            # Récupération des données du formulaire
            telephone = form.cleaned_data['telephone']
            email = form.cleaned_data['email']
            nom_complet = form.cleaned_data['nom_complet']

            # Création d’un utilisateur
            mot_de_passe = secrets.token_urlsafe(8)
            utilisateur = Utilisateurs.objects.create(
                username=telephone,
                email=email,
                telephone=telephone,
                first_name=nom_complet,  # Ou split pour first/last name
                password=make_password(mot_de_passe),
                etablissement=form.cleaned_data['etablissement'],
                role=Roles.objects.get_or_create(nom="Personnel")[0]
            )

            # Création du personnel
            personnel = form.save(commit=False)
            personnel.utilisateur = utilisateur
            personnel.save()

            # Envoi email ou SMS (facultatif)

            return redirect('liste_personnels')
    else:
        form = PersonnelForm()

    return render(request, 'backoffice/enseignants/personnels/form.html', {'form': form})

def export_enseignants_pdf(request):
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    enseignants = Personnels.objects.filter(etablissement=request.user.etablissement, actif=True)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="enseignants.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 50, "Liste des Enseignants")

    y = height - 80
    p.setFont("Helvetica", 10)
    p.drawString(30, y, "Nom complet")
    p.drawString(180, y, "Classe")
    p.drawString(300, y, "Poste")
    p.drawString(400, y, "Date embauche")
    p.drawString(500, y, "Statut")

    y -= 20

    for enseignant in enseignants:
        if y < 50:
            p.showPage()
            y = height - 50

        # Récupération de la classe enseignée (s’il y en a une)
        tenue = TenueDeClasse.objects.filter(
            enseignant=enseignant, 
            annee_scolaire=annee_active
        ).first()
        classe = tenue.classe.nom if tenue else ""

        p.drawString(30, y, enseignant.nom_complet)
        p.drawString(180, y, classe)
        p.drawString(300, y, enseignant.poste.nom if enseignant.poste else "")
        p.drawString(400, y, enseignant.date_embauche.strftime('%d/%m/%Y'))
        p.drawString(500, y, enseignant.get_statut_display())
        y -= 20

    p.showPage()
    p.save()
    return response




def export_enseignants_excel(request):
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    enseignants = Personnels.objects.filter(etablissement=request.user.etablissement, actif=True)

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="enseignants.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Enseignants')

    row_num = 0
    columns = ['Nom complet', 'Classe', 'Poste', 'Date embauche', 'Statut']

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title)

    for enseignant in enseignants:
        row_num += 1
        tenue = TenueDeClasse.objects.filter(
            enseignant=enseignant, 
            annee_scolaire=annee_active
        ).first()
        classe = tenue.classe.nom if tenue else ""

        ws.write(row_num, 0, enseignant.nom_complet)
        ws.write(row_num, 1, classe)
        ws.write(row_num, 2, enseignant.poste.nom if enseignant.poste else "")
        ws.write(row_num, 3, enseignant.date_embauche.strftime('%d/%m/%Y'))
        ws.write(row_num, 4, enseignant.get_statut_display())

    wb.save(response)
    return response



 # Back office enseignants-----------------------------------------------------------------------------------------------
def liste_personnels(request):
    personnels = Personnels.objects.all()
    return render(request, 'backoffice/enseignants/personnels/liste.html', {'personnels': personnels})

@fonctionnalite_autorisee('liste_personnels_secretariat') 
def liste_personnels_secretariat(request):
    personnels = Personnels.objects.filter(poste__nom__in=['Trésorière', 'Comptable'])
    return render(request, 'backoffice/enseignants/personnels/liste_secretrariat.html', {'personnels': personnels})

@fonctionnalite_autorisee('liste_personnels_etablissement') 
def liste_personnels_etablissement(request):
    personnels = Personnels.objects.filter(poste__nom__in=["Directeur d'Ecole", "Chef d'Etablissement"])
    return render(request, 'backoffice/enseignants/personnels/liste_directions.html', {'personnels': personnels})

@fonctionnalite_autorisee('liste_personnels_economat') 
def liste_personnels_economat(request):
    personnels = Personnels.objects.filter(poste__nom='Économe')
    return render(request, 'backoffice/enseignants/personnels/liste_econome.html', {'personnels': personnels})

@fonctionnalite_autorisee('liste_personnels_instituteurs') 
def liste_personnels_instituteurs(request):
    personnels = Personnels.objects.filter(poste__nom='Enseignant')
    return render(request, 'backoffice/enseignants/personnels/liste_adjoint.html', {'personnels': personnels})

@fonctionnalite_autorisee('liste_personnels_professeurs') 
def liste_personnels_professeurs(request):
    personnels = Personnels.objects.filter(poste__nom='Professeur')
    return render(request, 'backoffice/enseignants/personnels/liste_professeur.html', {'personnels': personnels})

def creer_personnel(request):
    form = PersonnelForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():
        personnel = form.save(commit=False)

        # Création automatique de l'utilisateur
        telephone = form.cleaned_data['telephone']
        email = form.cleaned_data['email']
        role = form.cleaned_data['role']  # Récupère le rôle sélectionné
        nom_complet = form.cleaned_data['nom_complet'].split()
        prenom = nom_complet[0]
        nom = " ".join(nom_complet[1:]) if len(nom_complet) > 1 else ''

        # Exemple : rôle par défaut "Personnel"
        #role_defaut = Roles.objects.get(nom="Personnel")

        utilisateur = Utilisateurs.objects.create(
            username=telephone,
            first_name=prenom,
            last_name=nom,
            etablissement=form.cleaned_data['etablissement'],
            photo=form.cleaned_data['photo'],
            role=role,  # Associe le rôle sélectionné
            email=email,
            telephone=telephone,
            pwd=telephone,
            password=make_password(telephone)  # Ou générer aléatoirement et envoyer par SMS/email
        )
        # Création du personnel
        personnel = form.save(commit=False)
        personnel.utilisateur = utilisateur
        personnel.save()

        # Envoi email ou SMS (facultatif)
        # ... après création de l'utilisateur ......................................................................
        #mot_de_passe = "MotDePasse123"  # ou mot de passe généré
        #send_mail(
        #    subject="Votre compte utilisateur a été créé",
        #    message=f"Bonjour {utilisateur.first_name},\n\nVotre compte a été créé.\nIdentifiant : {utilisateur.username}\nMot de passe : {mot_de_passe}\n\nMerci.",
        #    from_email=None,
        #    recipient_list=[utilisateur.email],  # Assurez-vous que le champ email est renseigné
        #    fail_silently=False,
        #)
        
        # ENVOI DE SMS (via une API comme Twilio) ..........................................................................
        #message = f"Bienvenue {utilisateur.first_name}, identifiant: {utilisateur.username}, mot de passe: {mot_de_passe}"
        #envoyer_sms(utilisateur.telephone, message)

        return redirect('liste_personnels')
    
    return render(request, 'backoffice/enseignants/personnels/form.html', {'form': form})

@fonctionnalite_autorisee('fonctionnalite_autorisee') 
def creer_personnel_secretariat(request):
    form = PersonnelSecreForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():
        personnel = form.save(commit=False)

        # Création automatique de l'utilisateur
        telephone = form.cleaned_data['telephone']
        email = form.cleaned_data['email']
        role = form.cleaned_data['role']  # Récupère le rôle sélectionné
        nom_complet = form.cleaned_data['nom_complet'].split()
        prenom = nom_complet[0]
        nom = " ".join(nom_complet[1:]) if len(nom_complet) > 1 else ''

        # Exemple : rôle par défaut "Personnel"
        #role_defaut = Roles.objects.get(nom="Personnel")

        utilisateur = Utilisateurs.objects.create(
            username=telephone,
            first_name=prenom,
            last_name=nom,
            etablissement=form.cleaned_data['etablissement'],
            photo=form.cleaned_data['photo'],
            role=role,  # Associe le rôle sélectionné
            email=email,
            telephone=telephone,
            pwd=telephone,
            password=make_password(telephone)  # Ou générer aléatoirement et envoyer par SMS/email
        )
        # Création du personnel
        personnel = form.save(commit=False)
        personnel.utilisateur = utilisateur
        personnel.save()

        # Envoi email ou SMS (facultatif)
        # ... après création de l'utilisateur ......................................................................
        #mot_de_passe = "MotDePasse123"  # ou mot de passe généré
        #send_mail(
        #    subject="Votre compte utilisateur a été créé",
        #    message=f"Bonjour {utilisateur.first_name},\n\nVotre compte a été créé.\nIdentifiant : {utilisateur.username}\nMot de passe : {mot_de_passe}\n\nMerci.",
        #    from_email=None,
        #    recipient_list=[utilisateur.email],  # Assurez-vous que le champ email est renseigné
        #    fail_silently=False,
        #)
        
        # ENVOI DE SMS (via une API comme Twilio) ..........................................................................
        #message = f"Bienvenue {utilisateur.first_name}, identifiant: {utilisateur.username}, mot de passe: {mot_de_passe}"
        #envoyer_sms(utilisateur.telephone, message)

        return redirect('liste_personnels_secretariat')
    
    return render(request, 'backoffice/enseignants/personnels/form.html', {'form': form})

@fonctionnalite_autorisee('fonctionnalite_autorisee') 
def creer_personnel_direction(request):
    form = PersonnelDirecForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():
        personnel = form.save(commit=False)

        # Création automatique de l'utilisateur
        telephone = form.cleaned_data['telephone']
        email = form.cleaned_data['email']
        role = form.cleaned_data['role']  # Récupère le rôle sélectionné
        nom_complet = form.cleaned_data['nom_complet'].split()
        prenom = nom_complet[0]
        nom = " ".join(nom_complet[1:]) if len(nom_complet) > 1 else ''

        # Exemple : rôle par défaut "Personnel"
        #role_defaut = Roles.objects.get(nom="Personnel")

        utilisateur = Utilisateurs.objects.create(
            username=telephone,
            first_name=prenom,
            last_name=nom,
            etablissement=form.cleaned_data['etablissement'],
            photo=form.cleaned_data['photo'],
            role=role,  # Associe le rôle sélectionné
            email=email,
            telephone=telephone,
            pwd=telephone,
            password=make_password(telephone)  # Ou générer aléatoirement et envoyer par SMS/email
        )
        # Création du personnel
        personnel = form.save(commit=False)
        personnel.utilisateur = utilisateur
        personnel.save()

        # Envoi email ou SMS (facultatif)
        # ... après création de l'utilisateur ......................................................................
        #mot_de_passe = "MotDePasse123"  # ou mot de passe généré
        #send_mail(
        #    subject="Votre compte utilisateur a été créé",
        #    message=f"Bonjour {utilisateur.first_name},\n\nVotre compte a été créé.\nIdentifiant : {utilisateur.username}\nMot de passe : {mot_de_passe}\n\nMerci.",
        #    from_email=None,
        #    recipient_list=[utilisateur.email],  # Assurez-vous que le champ email est renseigné
        #    fail_silently=False,
        #)
        
        # ENVOI DE SMS (via une API comme Twilio) ..........................................................................
        #message = f"Bienvenue {utilisateur.first_name}, identifiant: {utilisateur.username}, mot de passe: {mot_de_passe}"
        #envoyer_sms(utilisateur.telephone, message)

        return redirect('liste_personnels_etablissement')
    
    return render(request, 'backoffice/enseignants/personnels/form.html', {'form': form})

@fonctionnalite_autorisee('fonctionnalite_autorisee') 
def creer_personnel_economat(request):
    form = PersonnelEconForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():
        personnel = form.save(commit=False)

        # Création automatique de l'utilisateur
        telephone = form.cleaned_data['telephone']
        email = form.cleaned_data['email']
        role = form.cleaned_data['role']  # Récupère le rôle sélectionné
        nom_complet = form.cleaned_data['nom_complet'].split()
        prenom = nom_complet[0]
        nom = " ".join(nom_complet[1:]) if len(nom_complet) > 1 else ''

        # Exemple : rôle par défaut "Personnel"
        #role_defaut = Roles.objects.get(nom="Personnel")

        utilisateur = Utilisateurs.objects.create(
            username=telephone,
            first_name=prenom,
            last_name=nom,
            etablissement=form.cleaned_data['etablissement'],
            photo=form.cleaned_data['photo'],
            role=role,  # Associe le rôle sélectionné
            email=email,
            telephone=telephone,
            pwd=telephone,
            password=make_password(telephone)  # Ou générer aléatoirement et envoyer par SMS/email
        )
        # Création du personnel
        personnel = form.save(commit=False)
        personnel.utilisateur = utilisateur
        personnel.save()

        # Envoi email ou SMS (facultatif)
        # ... après création de l'utilisateur ......................................................................
        #mot_de_passe = "MotDePasse123"  # ou mot de passe généré
        #send_mail(
        #    subject="Votre compte utilisateur a été créé",
        #    message=f"Bonjour {utilisateur.first_name},\n\nVotre compte a été créé.\nIdentifiant : {utilisateur.username}\nMot de passe : {mot_de_passe}\n\nMerci.",
        #    from_email=None,
        #    recipient_list=[utilisateur.email],  # Assurez-vous que le champ email est renseigné
        #    fail_silently=False,
        #)
        
        # ENVOI DE SMS (via une API comme Twilio) ..........................................................................
        #message = f"Bienvenue {utilisateur.first_name}, identifiant: {utilisateur.username}, mot de passe: {mot_de_passe}"
        #envoyer_sms(utilisateur.telephone, message)

        return redirect('liste_personnels_economat')
    
    return render(request, 'backoffice/enseignants/personnels/form.html', {'form': form})

@fonctionnalite_autorisee('fonctionnalite_autorisee') 
def creer_personnel_professeur(request):
    form = PersonnelProfForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():
        personnel = form.save(commit=False)

        # Création automatique de l'utilisateur
        telephone = form.cleaned_data['telephone']
        email = form.cleaned_data['email']
        role = form.cleaned_data['role']  # Récupère le rôle sélectionné
        nom_complet = form.cleaned_data['nom_complet'].split()
        prenom = nom_complet[0]
        nom = " ".join(nom_complet[1:]) if len(nom_complet) > 1 else ''

        # Exemple : rôle par défaut "Personnel"
        #role_defaut = Roles.objects.get(nom="Personnel")

        utilisateur = Utilisateurs.objects.create(
            username=telephone,
            first_name=prenom,
            last_name=nom,
            etablissement=form.cleaned_data['etablissement'],
            photo=form.cleaned_data['photo'],
            role=role,  # Associe le rôle sélectionné
            email=email,
            telephone=telephone,
            pwd=telephone,
            password=make_password(telephone)  # Ou générer aléatoirement et envoyer par SMS/email
        )
        # Création du personnel
        personnel = form.save(commit=False)
        personnel.utilisateur = utilisateur
        personnel.save()

        # Envoi email ou SMS (facultatif)
        # ... après création de l'utilisateur ......................................................................
        #mot_de_passe = "MotDePasse123"  # ou mot de passe généré
        #send_mail(
        #    subject="Votre compte utilisateur a été créé",
        #    message=f"Bonjour {utilisateur.first_name},\n\nVotre compte a été créé.\nIdentifiant : {utilisateur.username}\nMot de passe : {mot_de_passe}\n\nMerci.",
        #    from_email=None,
        #    recipient_list=[utilisateur.email],  # Assurez-vous que le champ email est renseigné
        #    fail_silently=False,
        #)
        
        # ENVOI DE SMS (via une API comme Twilio) ..........................................................................
        #message = f"Bienvenue {utilisateur.first_name}, identifiant: {utilisateur.username}, mot de passe: {mot_de_passe}"
        #envoyer_sms(utilisateur.telephone, message)

        return redirect('liste_personnels_professeurs')
    
    return render(request, 'backoffice/enseignants/personnels/form.html', {'form': form})

@fonctionnalite_autorisee('creer_personnel_adjoint') 
def creer_personnel_adjoint(request):
    form = PersonnelAdjoiForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():
        personnel = form.save(commit=False)

        # Création automatique de l'utilisateur
        telephone = form.cleaned_data['telephone']
        email = form.cleaned_data['email']
        role = form.cleaned_data['role']  # Récupère le rôle sélectionné
        nom_complet = form.cleaned_data['nom_complet'].split()
        prenom = nom_complet[0]
        nom = " ".join(nom_complet[1:]) if len(nom_complet) > 1 else ''

        # Exemple : rôle par défaut "Personnel"
        #role_defaut = Roles.objects.get(nom="Personnel")

        utilisateur = Utilisateurs.objects.create(
            username=telephone,
            first_name=prenom,
            last_name=nom,
            etablissement=form.cleaned_data['etablissement'],
            photo=form.cleaned_data['photo'],
            role=role,  # Associe le rôle sélectionné
            email=email,
            telephone=telephone,
            pwd=telephone,
            password=make_password(telephone)  # Ou générer aléatoirement et envoyer par SMS/email
        )
        # Création du personnel
        personnel = form.save(commit=False)
        personnel.utilisateur = utilisateur
        personnel.save()

        # Envoi email ou SMS (facultatif)
        # ... après création de l'utilisateur ......................................................................
        #mot_de_passe = "MotDePasse123"  # ou mot de passe généré
        #send_mail(
        #    subject="Votre compte utilisateur a été créé",
        #    message=f"Bonjour {utilisateur.first_name},\n\nVotre compte a été créé.\nIdentifiant : {utilisateur.username}\nMot de passe : {mot_de_passe}\n\nMerci.",
        #    from_email=None,
        #    recipient_list=[utilisateur.email],  # Assurez-vous que le champ email est renseigné
        #    fail_silently=False,
        #)
        
        # ENVOI DE SMS (via une API comme Twilio) ..........................................................................
        #message = f"Bienvenue {utilisateur.first_name}, identifiant: {utilisateur.username}, mot de passe: {mot_de_passe}"
        #envoyer_sms(utilisateur.telephone, message)

        return redirect('liste_personnels_instituteurs')
    
    return render(request, 'backoffice/enseignants/personnels/form.html', {'form': form})

def envoyer_sms(telephone, message):
    account_sid = 'VOTRE_TWILIO_SID'
    auth_token = 'VOTRE_TWILIO_TOKEN'
    client = Client(account_sid, auth_token)

    client.messages.create(
        body=message,
        from_='+1XXXXXXXXXX',  # Numéro Twilio
        to=f'+225{telephone}'  # Adapté au format de votre pays
    )


def modifier_personnel(request, pk):
    personnel = get_object_or_404(Personnels, pk=pk)
    form = PersonnelForm(request.POST or None, request.FILES or None, instance=personnel)
    if form.is_valid():
        form.save()
        return redirect('liste_personnels')
    return render(request, 'backoffice/enseignants/personnels/form.html', {'form': form})

@fonctionnalite_autorisee('modifier_personnel_secretariat') 
def modifier_personnel_secretariat(request, pk):
    personnel = get_object_or_404(Personnels, pk=pk)
    form = PersonnelSecreForm(request.POST or None, request.FILES or None, instance=personnel)
    if form.is_valid():
        form.save()
        return redirect('liste_personnels_secretariat')
    return render(request, 'backoffice/enseignants/personnels/form.html', {'form': form})

@fonctionnalite_autorisee('modifier_personnel_etablissement') 
def modifier_personnel_etablissement(request, pk):
    personnel = get_object_or_404(Personnels, pk=pk)
    form = PersonnelDirecForm(request.POST or None, request.FILES or None, instance=personnel)
    if form.is_valid():
        form.save()
        return redirect('liste_personnels')
    return render(request, 'backoffice/enseignants/personnels/form.html', {'form': form})

@fonctionnalite_autorisee('modifier_personnel_economat') 
def modifier_personnel_economat(request, pk):
    personnel = get_object_or_404(Personnels, pk=pk)
    form = PersonnelEconForm(request.POST or None, request.FILES or None, instance=personnel)
    if form.is_valid():
        form.save()
        return redirect('liste_personnels_economat')
    return render(request, 'backoffice/enseignants/personnels/form.html', {'form': form})

@fonctionnalite_autorisee('modifier_personnel_adjoint') 
def modifier_personnel_adjoint(request, pk):
    personnel = get_object_or_404(Personnels, pk=pk)
    form = PersonnelAdjoiForm(request.POST or None, request.FILES or None, instance=personnel)
    if form.is_valid():
        form.save()
        return redirect('liste_personnels_instituteurs')
    return render(request, 'backoffice/enseignants/personnels/form.html', {'form': form})

@fonctionnalite_autorisee('modifier_personnel_professeur') 
def modifier_personnel_professeur(request, pk):
    personnel = get_object_or_404(Personnels, pk=pk)
    form = PersonnelProfForm(request.POST or None, request.FILES or None, instance=personnel)
    if form.is_valid():
        form.save()
        return redirect('liste_personnels_professeurs')
    return render(request, 'backoffice/enseignants/personnels/form.html', {'form': form})

def supprimer_personnel(request, pk):
    personnel = get_object_or_404(Personnels, pk=pk)
    if request.method == 'POST':
        personnel.delete()
        return redirect('liste_personnels')
    return render(request, 'backoffice/enseignants/personnels/confirm.html', {'objet': personnel})



# === MutationPersonnel ======================================================================================================================
def liste_mutations(request):
    mutations = MutationPersonnel.objects.all()
    return render(request, 'backoffice/enseignants/mutationpersonnels/liste.html', {'mutations': mutations})

def ajouter_mutation(request):
    if request.method == 'POST':
        form = MutationPersonnelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_mutations')
    else:
        form = MutationPersonnelForm()
    return render(request, 'backoffice/enseignants/mutationpersonnels/form.html', {'form': form, 'titre': 'Ajouter une mutation'})

def modifier_mutation(request, pk):
    mutation = get_object_or_404(MutationPersonnel, pk=pk)
    if request.method == 'POST':
        form = MutationPersonnelForm(request.POST, instance=mutation)
        if form.is_valid():
            form.save()
            return redirect('liste_mutations')
    else:
        form = MutationPersonnelForm(instance=mutation)
    return render(request, 'backoffice/enseignants/mutationpersonnels/form.html', {'form': form, 'titre': 'Modifier la mutation'})

def supprimer_mutation(request, pk):
    mutation = get_object_or_404(MutationPersonnel, pk=pk)
    if request.method == 'POST':
        mutation.delete()
        return redirect('liste_mutations')
    return render(request, 'backoffice/enseignants/mutationpersonnels/confirm.html', {'mutation': mutation})

# === TenueDeClasse ==========================================================================================================================
def liste_tenue_classe(request):
    tenues = TenueDeClasse.objects.all()
    return render(request, 'backoffice/enseignants/tenues/liste.html', {'tenues': tenues})

def ajouter_tenue_classe(request):
    if request.method == 'POST':
        form = TenueDeClasseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_tenue_classe')
    else:
        form = TenueDeClasseForm()
    return render(request, 'backoffice/enseignants/tenues/form.html', {'form': form, 'titre': 'Nouvelle tenue de classe'})

def modifier_tenue_classe(request, pk):
    tenue = get_object_or_404(TenueDeClasse, pk=pk)
    if request.method == 'POST':
        form = TenueDeClasseForm(request.POST, instance=tenue)
        if form.is_valid():
            form.save()
            return redirect('liste_tenue_classe')
    else:
        form = TenueDeClasseForm(instance=tenue)
    return render(request, 'backoffice/enseignants/tenues/form.html', {'form': form, 'titre': 'Modifier la tenue de classe'})

def supprimer_tenue_classe(request, pk):
    tenue = get_object_or_404(TenueDeClasse, pk=pk)
    if request.method == 'POST':
        tenue.delete()
        return redirect('liste_tenue_classe')
    return render(request, 'backoffice/enseignants/tenues/confirm.html', {'tenue': tenue})

# === Affectation ============================================================================================================================
def liste_affectations(request):
    affectations = Affectation.objects.all()
    return render(request, 'backoffice/enseignants/affectations/liste.html', {'affectations': affectations})

def ajouter_affectation(request):
    if request.method == 'POST':
        form = AffectationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_affectations')
    else:
        form = AffectationForm()
    return render(request, 'backoffice/enseignants/affectations/form.html', {'form': form, 'titre': 'Nouvelle affectation'})

def modifier_affectation(request, pk):
    affectation = get_object_or_404(Affectation, pk=pk)
    if request.method == 'POST':
        form = AffectationForm(request.POST, instance=affectation)
        if form.is_valid():
            form.save()
            return redirect('liste_affectations')
    else:
        form = AffectationForm(instance=affectation)
    return render(request, 'backoffice/enseignants/affectations/form.html', {'form': form, 'titre': 'Modifier l\'affectation'})

def supprimer_affectation(request, pk):
    affectation = get_object_or_404(Affectation, pk=pk)
    if request.method == 'POST':
        affectation.delete()
        return redirect('liste_affectations')
    return render(request, 'backoffice/enseignants/affectations/confirm.html', {'affectation': affectation})
