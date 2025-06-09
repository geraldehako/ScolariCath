# Récupérer les modalités pour un élève, selon son statut d'affectation
from authentifications.decorators import fonctionnalite_autorisee
from cores.models import AnneeScolaires
from eleves.models import Eleves, Inscriptions, Relances
from etablissements.models import Etablissements, Niveaux
from scolarites.forms import EcheanceForm, ModalitePaiementForm
from scolarites.models import ModalitePaiements

from django.shortcuts import render, get_object_or_404, redirect
from .models import ModaliteCantines, ModalitePaiements, Echeances, ModaliteTransports, Mois, PaiementsCantines, PaiementsTransports
from .forms import ModaliteCantineForm, ModalitePaiementsForm, EcheancesForm, ModaliteTransportForm, MoisForm, PaiementCantineForm, PaiementTransportForm

# === Mois associé aux Modalités de transport et cantine ==================================================================================================
def liste_mois(request):
    mois = Mois.objects.all()
    return render(request, 'backoffice/scolarites/mois/liste.html', {'mois_list': mois})

def creer_mois(request):
    form = MoisForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_mois')
    return render(request, 'backoffice/scolarites/mois/formulaire.html', {'form': form, 'titre': 'Créer un mois'})

def modifier_mois(request, pk):
    mois = get_object_or_404(Mois, pk=pk)
    form = MoisForm(request.POST or None, instance=mois)
    if form.is_valid():
        form.save()
        return redirect('liste_mois')
    return render(request, 'backoffice/scolarites/mois/formulaire.html', {'form': form, 'titre': 'Modifier le mois'})

def supprimer_mois(request, pk):
    mois = get_object_or_404(Mois, pk=pk)
    if request.method == 'POST':
        mois.delete()
        return redirect('liste_mois')
    return render(request, 'backoffice/scolarites/mois/confirm_delete.html', {'objet': mois})

# === Modalités de paiement ================================================================================================================================
def liste_modalites(request):
    modalites = ModalitePaiements.objects.all()
    return render(request, 'backoffice/scolarites/modalites/liste.html', {'modalites': modalites})

@fonctionnalite_autorisee('liste_modalites_etablissement_back')
def liste_modalites_etablissement_back(request, etablissement_id):
    etablissement = get_object_or_404(Etablissements, pk=etablissement_id)
    modalites = ModalitePaiements.objects.filter(etablissement=etablissement)

    return render(request, 'backoffice/scolarites/modalites/liste_modalites_back.html', {
        'etablissement': etablissement,
        'modalites': modalites
    })

@fonctionnalite_autorisee('detail_echeances_modalite_back') 
def detail_echeances_modalite_back(request, modalite_id):
    modalite = get_object_or_404(ModalitePaiements, pk=modalite_id)
    echeances = modalite.echeances_set.all()

    return render(request, 'backoffice/scolarites/modalites/detail_echeances_back.html', {
        'modalite': modalite,
        'echeances': echeances
    })
    
def creer_modalite(request):
    form = ModalitePaiementsForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_modalites')
    return render(request, 'blackoffice/scolarites/modalites/form.html', {'form': form})


def modifier_modalite(request, pk):
    modalite = get_object_or_404(ModalitePaiements, pk=pk)
    form = ModalitePaiementsForm(request.POST or None, instance=modalite)
    if form.is_valid():
        form.save()
        return redirect('liste_modalites')
    return render(request, 'blackoffice/scolarites/modalites/form.html', {'form': form})


def supprimer_modalite(request, pk):
    modalite = get_object_or_404(ModalitePaiements, pk=pk)
    if request.method == 'POST':
        modalite.delete()
        return redirect('liste_modalites')
    return render(request, 'blackoffice/scolarites/modalites/confirm.html', {'objet': modalite})


def detail_modalite(request, pk):
    modalite = get_object_or_404(ModalitePaiements, pk=pk)
    echeances = Echeances.objects.filter(modalite=modalite)
    return render(request, 'blackoffice/scolarites/modalites/detail.html', {
        'modalite': modalite,
        'echeances': echeances
    })

from django.db import IntegrityError
from django.contrib import messages  # Pour afficher une alerte

def afficher_niveaux_et_modalites(request, etablissement_id):
    etablissement = get_object_or_404(Etablissements, pk=etablissement_id)
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    niveaux = Niveaux.objects.filter(cycle__in=etablissement.types.all())

    if request.method == 'POST':
        niveau_id = request.POST.get('niveau')
        niveau = get_object_or_404(Niveaux, pk=niveau_id)
        # Récupération correcte du booléen
        applicable_aux_non_affectes = request.POST.get('applicable_aux_non_affectes') == 'on'
        
        form = ModalitePaiementForm(request.POST)
        if form.is_valid():
            # Vérification si une modalité similaire existe déjà
            if ModalitePaiements.objects.filter(
                etablissement=etablissement,
                annee_scolaire=annee_active,
                niveau=niveau,
                applicable_aux_non_affectes=applicable_aux_non_affectes
            ).exists():
                messages.warning(request,  f"❌ Une modalité de paiement existe déjà pour le niveau {niveau.nom} en {annee_active.libelle}, "
                    f"{'applicable aux non affectés' if applicable_aux_non_affectes else 'applicable aux affectés'}.")
            else:
                try:
                    modalite = form.save(commit=False)
                    modalite.annee_scolaire = annee_active
                    modalite.etablissement = etablissement
                    modalite.niveau = niveau
                    modalite.applicable_aux_non_affectes = applicable_aux_non_affectes
                    modalite.save()
                    modalite.generer_echeances()
                    return redirect('modifier_echeances_modalite', modalite_id=modalite.id)
                except IntegrityError:
                    messages.error(request, "Erreur d’intégrité lors de la création de la modalité.")
    else:
        form = ModalitePaiementForm(initial={'etablissement': etablissement}) 

    return render(request, 'backoffice/scolarites/modalites/afficher_niveaux_modalites.html', {
        'etablissement': etablissement,
        'niveaux': niveaux,
        'form': form
    })

@fonctionnalite_autorisee('modalites_cantine')
def modalites_cantine(request, etab_id):
    etablissement = get_object_or_404(Etablissements, id=etab_id)
    annee_active = get_object_or_404(AnneeScolaires, active=True)
    modalites = ModaliteCantines.objects.filter(etablissement=etablissement, annee_scolaire=annee_active)
    return render(request, 'backoffice/scolarites/modalites/cantines/cantine_liste.html', {
        'etablissement': etablissement,
        'modalites': modalites
    })

@fonctionnalite_autorisee('ajouter_modalite_cantine')
def ajouter_modalite_cantine(request, etab_id):
    etablissement = get_object_or_404(Etablissements, id=etab_id)
    annee_active = get_object_or_404(AnneeScolaires, active=True)

    if request.method == 'POST':
        form = ModaliteCantineForm(request.POST)
        if form.is_valid():
            modalite = form.save(commit=False)
            modalite.etablissement = etablissement
            modalite.annee_scolaire = annee_active
            modalite.save()
            return redirect('modalites_cantine', etab_id=etab_id)
    else:
        form = ModaliteCantineForm()

    return render(request, 'backoffice/scolarites/modalites/cantines/cantine_form.html', {
        'form': form,
        'etablissement': etablissement
    })

@fonctionnalite_autorisee('modifier_modalite_cantine')
def modifier_modalite_cantine(request, id):
    modalite = get_object_or_404(ModaliteCantines, id=id)
    if request.method == 'POST':
        form = ModaliteCantineForm(request.POST, instance=modalite)
        if form.is_valid():
            form.save()
            return redirect('modalites_cantine', etab_id=modalite.etablissement.id)
    else:
        form = ModaliteCantineForm(instance=modalite)
    return render(request, 'backoffice/scolarites/modalites/cantines/modifier.html', {'form': form, 'modalite': modalite})

@fonctionnalite_autorisee('supprimer_modalite_cantine')
def supprimer_modalite_cantine(request, id):
    modalite = get_object_or_404(ModaliteCantines, id=id)
    etab_id = modalite.etablissement.id
    modalite.delete()
    return redirect('modalites_cantine', etab_id=etab_id)

@fonctionnalite_autorisee('modalites_transport')
def modalites_transport(request, etab_id):
    etablissement = get_object_or_404(Etablissements, id=etab_id)
    annee_active = get_object_or_404(AnneeScolaires, active=True)
    modalites = ModaliteTransports.objects.filter(etablissement=etablissement, annee_scolaire=annee_active)
    return render(request, 'backoffice/scolarites/modalites/transports/transport_liste.html', {
        'etablissement': etablissement,
        'modalites': modalites
    })
    
from django.db import IntegrityError
from django.contrib import messages

@fonctionnalite_autorisee('ajouter_modalite_transport')
def ajouter_modalite_transport(request, etab_id):
    etablissement = get_object_or_404(Etablissements, id=etab_id)
    annee_active = get_object_or_404(AnneeScolaires, active=True)

    if request.method == 'POST':
        form = ModaliteTransportForm(request.POST)
        if form.is_valid():
            modalite = form.save(commit=False)
            modalite.etablissement = etablissement
            modalite.annee_scolaire = annee_active
            try:
                modalite.save()
                messages.success(request, "Modalité de transport ajoutée avec succès.")
                return redirect('modalites_transport', etab_id=etab_id)
            except IntegrityError:
                form.add_error(None, "❌ Une modalité de transport pour ce mois existe déjà pour cet établissement et cette année scolaire.")
    else:
        form = ModaliteTransportForm()

    return render(request, 'backoffice/scolarites/modalites/transports/transport_form.html', {
        'form': form,
        'etablissement': etablissement
    })

@fonctionnalite_autorisee('modifier_modalite_transport')   
def modifier_modalite_transport(request, id):
    modalite = get_object_or_404(ModaliteTransports, id=id)
    if request.method == 'POST':
        form = ModaliteTransportForm(request.POST, instance=modalite)
        if form.is_valid():
            form.save()
            return redirect('modalites_transport', etab_id=modalite.etablissement.id)
    else:
        form = ModaliteTransportForm(instance=modalite)
    return render(request, 'backoffice/scolarites/modalites/transports/modifier.html', {'form': form, 'modalite': modalite})

@fonctionnalite_autorisee('supprimer_modalite_transport')
def supprimer_modalite_transport(request, id):
    modalite = get_object_or_404(ModaliteTransports, id=id)
    etab_id = modalite.etablissement.id
    modalite.delete()
    return redirect('modalites_transport', etab_id=etab_id)


def afficher_niveaux_et_modalitesOK(request, etablissement_id):
    etablissement = get_object_or_404(Etablissements, pk=etablissement_id)
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    
    # Récupérer les niveaux associés à l'établissement via les types
    # Assumons qu'il existe une relation entre Niveaux et TypeEtablissement ou une autre logique
    niveaux = Niveaux.objects.filter(cycle__in=etablissement.types.all())  # Utiliser 'in' pour filtrer sur plusieurs types associés à l'établissement
    
    if request.method == 'POST':
        # Récupérer le niveau sélectionné et le formulaire
        niveau_id = request.POST.get('niveau')  # Le niveau sélectionné
        niveau = get_object_or_404(Niveaux, pk=niveau_id)

        form = ModalitePaiementForm(request.POST)
        if form.is_valid():
            modalite = form.save(commit=False)
            modalite.annee_scolaire = annee_active  # Associer la modalité à l'établissement
            modalite.etablissement = etablissement  # Associer la modalité à l'établissement
            modalite.niveau = niveau  # Associer la modalité au niveau sélectionné
            modalite.save()
            modalite.generer_echeances()  # 👈 Auto-répartition ici

            #return redirect('afficher_niveaux_et_modalites', etablissement_id=etablissement.id)  # Rediriger vers la même page pour actualiser
            return redirect('modifier_echeances_modalite', modalite_id=modalite.id)


    else:
        form = ModalitePaiementForm(initial={'etablissement': etablissement}) 

    return render(request, 'backoffice/scolarites/modalites/afficher_niveaux_modalites.html', {
        'etablissement': etablissement,
        'niveaux': niveaux,
        'form': form
    })

# views.py
from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from .models import ModalitePaiements, Echeances
from .forms import EcheanceForm

@fonctionnalite_autorisee('modifier_echeances_modalite')
def modifier_echeances_modalite(request, modalite_id):
    modalite = get_object_or_404(ModalitePaiements, id=modalite_id)
    EcheanceFormSet = modelformset_factory(Echeances, form=EcheanceForm, extra=0)

    queryset = Echeances.objects.filter(modalite=modalite)
    formset = EcheanceFormSet(queryset=queryset)

    erreur_montant = None

    if request.method == 'POST':
        formset = EcheanceFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            # Calcul de la somme des montants
            montant_total = 0
            for form in formset:
                montant = form.cleaned_data.get('montant')
                if montant is not None:
                    montant_total += montant

            # Vérifie que le total correspond au montant de la modalité
            if montant_total != modalite.montant:
                erreur_montant = f"Le total des échéances ({montant_total} FCFA) est différent du montant de la modalité ({modalite.montant} FCFA)."
            else:
                formset.save()
                return redirect('afficher_niveaux_et_modalites', etablissement_id=modalite.etablissement.id)
        else:
            print("Formset invalide :", formset.errors)

    return render(request, 'backoffice/scolarites/echeances/modifier_echeances.html', {
        'modalite': modalite,
        'formset': formset,
        'erreur_montant': erreur_montant
    })

# === Échéances ====================================================================================================================================
def liste_echeances(request):
    echeances = Echeances.objects.all()
    return render(request, 'blackoffice/scolarites/echeances/liste.html', {'echeances': echeances})


def creer_echeance(request):
    form = EcheancesForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_echeances')
    return render(request, 'blackoffice/scolarites/echeances/form.html', {'form': form})


def ajouter_echeance(request, modalite_id):
    modalite = get_object_or_404(ModalitePaiements, pk=modalite_id)

    if request.method == 'POST':
        form = EcheanceForm(request.POST)
        if form.is_valid():
            echeance = form.save(commit=False)
            echeance.modalite = modalite  # Lier l'échéance à la modalité actuelle
            echeance.save()
            return redirect('detail_modalite', pk=modalite.id)
    else:
        form = EcheanceForm()

    return render(request, 'blackoffice/scolarites/modalites/ajouter_echeance.html', {'form': form, 'modalite': modalite})


def modifier_echeance(request, pk):
    echeance = get_object_or_404(Echeances, pk=pk)
    form = EcheancesForm(request.POST or None, instance=echeance)
    if form.is_valid():
        form.save()
        return redirect('liste_echeances')
    return render(request, 'blackoffice/scolarites/echeances/form.html', {'form': form})


def supprimer_echeance(request, pk):
    echeance = get_object_or_404(Echeances, pk=pk)
    if request.method == 'POST':
        echeance.delete()
        return redirect('liste_echeances')
    return render(request, 'blackoffice/scolarites/echeances/confirm.html', {'objet': echeance})

# === Éxemple =========================================================================================
def get_modalites_paiement_for_eleve(eleve):
    if eleve.est_affecte:  # Si l'élève est affecté
        modalites = ModalitePaiements.objects.filter(etablissement=eleve.etablissement, annee_scolaire=eleve.annee_scolaire)
    else:  # Si l'élève est non affecté
        modalites = ModalitePaiements.objects.filter(
            etablissement=eleve.etablissement, 
            annee_scolaire=eleve.annee_scolaire, 
            applicable_aux_non_affectes=True
        )
    return modalites


from django.shortcuts import redirect, render, get_object_or_404
from .forms import PaiementEleveForm


def choisir_modalite_paiement(request, eleve_id):
    eleve = get_object_or_404(Eleves, pk=eleve_id)

    form = PaiementEleveForm(request.POST or None, eleve=eleve)

    if form.is_valid():
        modalite = form.cleaned_data['modalite']
        # Tu peux maintenant traiter le paiement...
        return redirect('confirmation_paiement')

    return render(request, 'paiement/choix_modalite.html', {
        'form': form,
        'eleve': eleve
    })



#  PAIEMENT ===========================================================================================================================================
from scolarites.forms import PaiementForm




from django.utils import timezone
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render, redirect

def ajouter_paiementA(request, inscription_id):
    inscription = get_object_or_404(Inscriptions, pk=inscription_id)

    total_du = inscription.montant_total_du()
    total_paye = inscription.montant_total_paye()
    solde = inscription.solde_restant()

    # Déplacer ici le calcul des montants déjà payés
    montants_payes_par_echeance = {}
    for echeance in inscription.echeances_non_soldees():
        total_paye_echeance = Paiements.objects.filter(
            inscription=inscription,
            echeance=echeance,
            statut_validation='partiel'
        ).aggregate(total=Sum('montant'))['total'] or 0
        montants_payes_par_echeance[echeance.id] = total_paye_echeance

    if request.method == 'POST':
        form = PaiementMultipleForm(request.POST, inscription=inscription)
        if form.is_valid():
            mode = form.cleaned_data['mode_paiement']
            for echeance, field_name in form.echeance_fields:
                montant = form.cleaned_data.get(field_name)
                if montant and montant > 0:
                    montant_restant = echeance.montant - montants_payes_par_echeance.get(echeance.id, 0)

                    # Déterminer le statut de validation
                    if montant >= montant_restant:
                        statut_validation = 'valide'
                    else:
                        statut_validation = 'partiel' if mode == 'especes' else 'en_attente'

                    Paiements.objects.create(
                        inscription=inscription,
                        echeance=echeance,
                        montant=montant,
                        date_paiement=timezone.now().date(),
                        mode_paiement=mode,
                        statut_validation=statut_validation,
                        valide_par=request.user if mode == 'especes' and statut_validation == 'valide' else None
                    )

            return redirect('detail_paiement', eleve_id=inscription.eleve.id)
    else:
        form = PaiementMultipleForm(inscription=inscription)

    return render(request, 'frontoffice/paiements/formulaire_paiement.html', {
        'form': form,
        'inscription': inscription,
        'total_du': total_du,
        'total_paye': total_paye,
        'solde': solde,
        'montants_payes': montants_payes_par_echeance,
    })


def ajouter_paiementBONJEUDI(request, inscription_id):
    inscription = get_object_or_404(Inscriptions, pk=inscription_id)

    total_du = inscription.montant_total_du()
    total_paye = inscription.montant_total_paye()
    solde = inscription.solde_restant()

    # Déplacer ici le calcul des montants déjà payés
    montants_payes_par_echeance = {}
    for echeance in inscription.echeances_non_soldees():
        total_paye_echeance = Paiements.objects.filter(
            inscription=inscription,
            echeance=echeance,
            statut_validation='partiel'
        ).aggregate(total=Sum('montant'))['total'] or 0
        montants_payes_par_echeance[echeance.id] = total_paye_echeance

    if request.method == 'POST':
        form = PaiementMultipleForm(request.POST, inscription=inscription)
        if form.is_valid():
            mode = form.cleaned_data['mode_paiement']
            for echeance, field_name in form.echeance_fields:
                montant = form.cleaned_data.get(field_name)
                if montant and montant > 0:
                    montant_restant = echeance.montant - montants_payes_par_echeance.get(echeance.id, 0)

                    # Déterminer le statut de validation
                    if montant >= montant_restant:
                        statut_validation = 'valide'
                    else:
                        statut_validation = 'partiel' if mode == 'especes' else 'en_attente'

                    Paiements.objects.create(
                        inscription=inscription,
                        echeance=echeance,
                        montant=montant,
                        date_paiement=timezone.now().date(),
                        mode_paiement=mode,
                        statut_validation=statut_validation,
                        valide_par=request.user if mode == 'especes' and statut_validation == 'valide' else None
                    )

            return redirect('detail_paiement', eleve_id=inscription.eleve.id)
    else:
        form = PaiementMultipleForm(inscription=inscription)

    return render(request, 'frontoffice/paiements/formulaire_paiement.html', {
        'form': form,
        'inscription': inscription,
        'total_du': total_du,
        'total_paye': total_paye,
        'solde': solde,
        'montants_payes': montants_payes_par_echeance,
    })

from django.db.models import Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from .models import  Paiements
from .forms import PaiementMultipleForm

@fonctionnalite_autorisee('ajouter_paiement')
def ajouter_paiement(request, inscription_id):
    inscription = get_object_or_404(Inscriptions, pk=inscription_id)

    total_du = inscription.montant_total_du()
    total_paye = inscription.montant_total_paye()
    solde = inscription.solde_restant()

    # Récupérer les relances actives pour cette inscription
    relances_actives = Relances.objects.filter(inscription=inscription, statut='active')

    # Calcul des montants déjà versés par relance
    montants_payes_par_relance = {}
    for relance in relances_actives:
        total_paye_relance = Paiements.objects.filter(
            inscription=inscription,
            echeance=relance.echeance,
            statut_validation='partiel'
        ).aggregate(total=Sum('montant'))['total'] or 0
        montants_payes_par_relance[relance.id] = total_paye_relance

    if request.method == 'POST':
        form = PaiementMultipleForm(request.POST, inscription=inscription)
        if form.is_valid():
            mode = form.cleaned_data['mode_paiement']
            numero_transaction = form.cleaned_data.get('numero_transaction')
            justificatif = request.FILES.get('justificatif')
            for relance, field_name in form.relance_fields:  # ⚠️ Assurez-vous que le formulaire utilise relance_fields
                montant = form.cleaned_data.get(field_name)
                if montant and montant > 0:
                    montant_restant = relance.echeance_montant - montants_payes_par_relance.get(relance.id, 0)

                    # Déterminer le statut de validation
                    if montant >= montant_restant:
                        statut_validation = 'valide'
                    else:
                        statut_validation = 'partiel' # if mode == 'especes' else 'en_attente' 

                    # Créer le paiement
                    Paiements.objects.create(
                        inscription=inscription,
                        echeance=relance.echeance,
                        montant=montant,
                        date_paiement=timezone.now().date(),
                        mode_paiement=mode,
                        numero_transaction=numero_transaction,
                        justificatif=justificatif,
                        statut_validation=statut_validation,
                        valide_par=request.user # if mode == 'especes' and statut_validation == 'valide' else None
                    )

                    # Mettre à jour la relance
                    relance.total_verse = (relance.total_verse or 0) + montant
                    relance.total_solde = max(relance.echeance_montant - relance.total_verse, 0)
                    relance.save()

            #return redirect('detail_paiement', eleve_id=inscription.eleve.id)
            #return redirect('recu_paiement_pdf', inscription_id=inscription.id)
            return redirect(f"{reverse('detail_paiement', kwargs={'eleve_id': inscription.eleve.id})}?recu=1")


    else:
        form = PaiementMultipleForm(inscription=inscription)

    return render(request, 'frontoffice/paiements/formulaire_paiement.html', {
        'form': form,
        'inscription': inscription,
        'total_du': total_du,
        'total_paye': total_paye,
        'solde': solde,
        'montants_payes': montants_payes_par_relance,
        'relances': relances_actives,
    })


from django.http import JsonResponse, Http404

@fonctionnalite_autorisee('cantine_non_payees')
def cantine_non_payees(request, eleve_id):
    try:
        inscription = Inscriptions.objects.get(
            eleve_id=eleve_id,
            annee_scolaire__active=True,
            cantine=True
        )
        print(inscription)
    except Inscriptions.DoesNotExist:
        return render(request, 'errors/erreur_modal.html', {
            'message': "Aucune inscription active avec cantine pour cet élève."
        })

    modalites = ModaliteCantines.objects.filter(
        etablissement=inscription.classe.etablissement,
        annee_scolaire=inscription.annee_scolaire,
    ).exclude(
        id__in=PaiementsCantines.objects.filter(inscription=inscription).values_list('echeance_id', flat=True)
    )

    if request.method == 'POST':
        form = PaiementCantineForm(request.POST, request.FILES, inscription=inscription, modalites=modalites)
        if form.is_valid():
            form.save(user=request.user)
            return redirect('detail_paiement', eleve_id=inscription.eleve.id)  # Redirection correcte
    else:
        form = PaiementCantineForm(inscription=inscription, modalites=modalites)

    total_du = sum(modalite.montant for modalite in modalites)
    total_paye = PaiementsCantines.objects.filter(inscription=inscription).aggregate(Sum('montant'))['montant__sum'] or 0
    solde = total_du # - total_paye

    return render(request, 'frontoffice/paiements/cantine_formulaire.html', {
        'inscription': inscription,
        'form': form,
        'total_du': total_du,
        'total_paye': total_paye,
        'solde': solde,
    })

@fonctionnalite_autorisee('transport_non_payees')
def transport_non_payees(request, eleve_id):
    try:
        inscription = Inscriptions.objects.get(
            eleve_id=eleve_id,
            annee_scolaire__active=True,
            transport=True
        )
       
    except Inscriptions.DoesNotExist:
        return render(request, 'errors/erreur_modal.html', {
            'message': "Aucune inscription active avec transport pour cet élève."
        })

    modalites = ModaliteTransports.objects.filter(
        etablissement=inscription.classe.etablissement,
        annee_scolaire=inscription.annee_scolaire,
    ).exclude(
        id__in=PaiementsTransports.objects.filter(inscription=inscription).values_list('echeance_id', flat=True)
    )

    if request.method == 'POST':
        form = PaiementTransportForm(request.POST, request.FILES, inscription=inscription, modalites=modalites)
        if form.is_valid():
            form.save(user=request.user)
            return redirect('detail_paiement', eleve_id=inscription.eleve.id)  # Redirection correcte
    else:
        form = PaiementTransportForm(inscription=inscription, modalites=modalites)

    total_du = sum(modalite.montant for modalite in modalites)
    total_paye = PaiementsTransports.objects.filter(inscription=inscription).aggregate(Sum('montant'))['montant__sum'] or 0
    solde = total_du # - total_paye

    return render(request, 'frontoffice/paiements/transport_formulaire.html', {
        'inscription': inscription,
        'form': form,
        'total_du': total_du,
        'total_paye': total_paye,
        'solde': solde,
    })


from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa  # Assure-toi que cette lib est installée : `pip install xhtml2pdf`

def recu_paiement_pdf(request, inscription_id):
    inscription = get_object_or_404(Inscriptions, pk=inscription_id)
    paiement = Paiements.objects.filter(inscription=inscription).order_by('-id').first()
    etablissement = request.user.etablissement
    # Utilisation dans le contexte :
    logo_path = etablissement.logo.path if etablissement.logo else None
    template = get_template('frontoffice/paiements/recu_paiement.html')
    html = template.render({
        'inscription': inscription,
        #'paiements': paiements,
        'paiement': paiement,  # (sans 's')
        'etablissement' : etablissement,
        'eleve': inscription.eleve,
        'logo_path': logo_path,  # <- Ajouté
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recu_{inscription.eleve.matricule}.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response


def ajouter_paiement_parentOK(request, inscription_id):
    inscription = get_object_or_404(Inscriptions, pk=inscription_id)

    total_du = inscription.montant_total_du()
    total_paye = inscription.montant_total_paye()
    solde = inscription.solde_restant()

    # Récupérer les relances actives pour cette inscription
    relances_actives = Relances.objects.filter(inscription=inscription, statut='active')

    # Calcul des montants déjà versés par relance
    montants_payes_par_relance = {}
    for relance in relances_actives:
        total_paye_relance = Paiements.objects.filter(
            inscription=inscription,
            echeance=relance.echeance,
            statut_validation='partiel'
        ).aggregate(total=Sum('montant'))['total'] or 0
        montants_payes_par_relance[relance.id] = total_paye_relance

    if request.method == 'POST':
        form = PaiementMultipleForm(request.POST, inscription=inscription)
        if form.is_valid():
            mode = form.cleaned_data['mode_paiement']
            for relance, field_name in form.relance_fields:  # ⚠️ Assurez-vous que le formulaire utilise relance_fields
                montant = form.cleaned_data.get(field_name)
                if montant and montant > 0:
                    montant_restant = relance.echeance_montant - montants_payes_par_relance.get(relance.id, 0)

                    # Déterminer le statut de validation
                    if montant >= montant_restant:
                        statut_validation = 'valide'
                    else:
                        statut_validation = 'partiel' if mode == 'especes' else 'en_attente'

                    # Créer le paiement
                    Paiements.objects.create(
                        inscription=inscription,
                        echeance=relance.echeance,
                        montant=montant,
                        date_paiement=timezone.now().date(),
                        mode_paiement=mode,
                        statut_validation=statut_validation,
                        valide_par=request.user if mode == 'especes' and statut_validation == 'valide' else None
                    )

                    # Mettre à jour la relance
                    relance.total_verse = (relance.total_verse or 0) + montant
                    relance.total_solde = max(relance.echeance_montant - relance.total_verse, 0)
                    relance.save()

            return redirect('detail_paiement', eleve_id=inscription.eleve.id)
    else:
        form = PaiementMultipleForm(inscription=inscription)

    return render(request, 'espace_parent/formulaire_paiement.html', {
        'form': form,
        'inscription': inscription,
        'total_du': total_du,
        'total_paye': total_paye,
        'solde': solde,
        'montants_payes': montants_payes_par_relance,
        'relances': relances_actives,
    })


from django.db.models import Sum
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
import uuid


from .forms import PaiementMultipleForm
@fonctionnalite_autorisee('bulletins_eleve')  
def ajouter_paiement_parent(request, inscription_id):
    inscription = get_object_or_404(Inscriptions, pk=inscription_id)

    total_du = inscription.montant_total_du()
    total_paye = inscription.montant_total_paye()
    solde = inscription.solde_restant()

    relances_actives = Relances.objects.filter(inscription=inscription, statut='active')

    montants_payes_par_relance = {}
    for relance in relances_actives:
        total_paye_relance = Paiements.objects.filter(
            inscription=inscription,
            echeance=relance.echeance,
            statut_validation='partiel'
        ).aggregate(total=Sum('montant'))['total'] or 0
        montants_payes_par_relance[relance.id] = total_paye_relance

    if request.method == 'POST':
        form = PaiementMultipleForm(request.POST, inscription=inscription)
        if form.is_valid():
            mode = form.cleaned_data['mode_paiement']
            paiements_temp = []
            total_saisi = 0

            for relance, field_name in form.relance_fields:
                montant = form.cleaned_data.get(field_name)
                if montant and montant > 0:
                    montant_restant = relance.echeance_montant - montants_payes_par_relance.get(relance.id, 0)

                    if montant >= montant_restant:
                        statut_validation = 'valide'
                    else:
                        statut_validation = 'partiel' if mode == 'especes' else 'en_attente'

                    paiement_data = {
                        'relance': relance,
                        'montant': montant,
                        'statut_validation': statut_validation,
                        'montant_restant': montant_restant,
                    }

                    paiements_temp.append(paiement_data)
                    total_saisi += montant

            if mode == 'mobile_money' and total_saisi > 0:
                transaction_id = str(uuid.uuid4()).replace('-', '')
                return_url = request.build_absolute_uri(reverse('detail_paiement', args=[inscription.eleve.id]))
                notify_url = request.build_absolute_uri(reverse('cinetpay_notify'))

                response = init_cinetpay_payment(
                    inscription, total_saisi, transaction_id, return_url, notify_url
                )

                payment_url = response.get("data", {}).get("payment_url")
                if payment_url:
                    # Enregistre les paiements en attente si besoin dans un modèle temporaire ici
                    request.session['paiements_mobile_money'] = [
                        {
                            'relance_id': p['relance'].id,
                            'montant': p['montant'],
                            'statut_validation': p['statut_validation'],
                            'transaction_id': transaction_id,
                            'inscription_id': inscription.id
                        }
                        for p in paiements_temp
                    ]
                    return redirect(payment_url)
                else:
                    messages.error(request, "Erreur de connexion à CinetPay : {}".format(response.get("message")))
            else:
                # Paiement en espèces : traitement immédiat
                for p in paiements_temp:
                    Paiements.objects.create(
                        inscription=inscription,
                        echeance=p['relance'].echeance,
                        montant=p['montant'],
                        date_paiement=timezone.now().date(),
                        mode_paiement=mode,
                        statut_validation=p['statut_validation'],
                        valide_par=request.user if p['statut_validation'] == 'valide' else None
                    )

                    # Mise à jour relance
                    relance = p['relance']
                    relance.total_verse = (relance.total_verse or 0) + p['montant']
                    relance.total_solde = max(relance.echeance_montant - relance.total_verse, 0)
                    relance.save()

                return redirect('detail_paiement', eleve_id=inscription.eleve.id)
    else:
        form = PaiementMultipleForm(inscription=inscription)

    return render(request, 'espace_parent/formulaire_paiement.html', {
        'form': form,
        'inscription': inscription,
        'total_du': total_du,
        'total_paye': total_paye,
        'solde': solde,
        'montants_payes': montants_payes_par_relance,
        'relances': relances_actives,
    })


from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from services.cinetpay import client, init_cinetpay_payment

@csrf_exempt
def cinetpay_notify(request):
    if request.method == 'POST':
        transaction_id = request.POST.get("transaction_id")
        if transaction_id:
            response = client.TransactionVerfication_trx(transaction_id)
            status = response.get("data", {}).get("status")

            if status == "ACCEPTED":
                # Enregistre le paiement comme "valide"
                # Tu peux stocker des infos liées au transaction_id temporairement dans un modèle
                ...
                return HttpResponse("Paiement confirmé", status=200)
            else:
                return HttpResponse("Paiement refusé", status=400)
    return HttpResponse("Aucune donnée", status=400)

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import uuid
import json

@csrf_exempt
def init_cinetpay_view(request):
    print("✅ Vue init_cinetpay_view appelée")
    if request.method != 'POST':
        return JsonResponse({'error': True, 'message': 'Méthode non autorisée'}, status=405)

    try:
        data = json.loads(request.body)
        inscription_id = data.get('inscription_id')
        montant = data.get('montant')

        if not inscription_id or not montant:
            return JsonResponse({'error': True, 'message': 'Champs requis manquants'}, status=400)

        return init_cinetpay(inscription_id, montant)

    except Exception as e:
        return JsonResponse({'error': True, 'message': str(e)}, status=500)

def init_cinetpay5(inscription_id, montant):
    import requests
    import uuid
    from django.conf import settings

    transaction_id = str(uuid.uuid4())

    payload = {
        "transaction_id": transaction_id,
        "amount": montant,
        "currency": "XOF",
        "site_id": settings.CINETPAY_SITE_ID,
        "apikey": settings.CINETPAY_API_KEY,
        "description": f"Paiement de la scolarité - ID inscription {inscription_id}",
        "notify_url": "https://tonsite.com/api/cinetpay/notify/",
        "return_url": "https://tonsite.com/paiement/success/",
        "customer_name": "Parent",
        "customer_email": "parent@exemple.com",
    }

    try:
        response = requests.post("https://api-checkout.cinetpay.com/v2/payment", json=payload)
        result = response.json()
        print("→ Réponse CinetPay : ", result)

        if result.get("code") == "201" and "data" in result:
            return JsonResponse({"url": result["data"]["payment_url"]})
        else:
            return JsonResponse({
                "error": True,
                "code": result.get("code"),
                "message": result.get("message"),
                "description": result.get("description"),
            }, status=400)

    except Exception as e:
        print("Exception CinetPay:", e)
        return JsonResponse({"error": True, "message": str(e)}, status=500)


def init_cinetpay(inscription_id, montant):
    import requests
    import uuid
    from django.conf import settings

    transaction_id = str(uuid.uuid4())

    payload = {
        "transaction_id": transaction_id,
        "amount": montant,
        "currency": "XOF",
        "site_id": settings.CINETPAY_SITE_ID,
        "apikey": settings.CINETPAY_API_KEY,
        "description": f"Paiement de la scolarité - ID inscription {inscription_id}",
        "notify_url": "https://tonsite.com/api/cinetpay/notify/",
        "return_url": "https://tonsite.com/paiement/success/",
        "customer_name": "Parent",
        "customer_email": "parent@exemple.com",
    }

    try:
        response = requests.post("https://api-checkout.cinetpay.com/v2/payment", json=payload)
        result = response.json()
        print("→ Réponse CinetPay : ", result)

        if result.get("code") == "201" and "data" in result:
            return JsonResponse({"url": result["data"]["payment_url"]})
        else:
            return JsonResponse({
                "error": True,
                "code": result.get("code"),
                "message": result.get("message"),
                "description": result.get("description"),
            }, status=400)

    except Exception as e:
        print("Exception CinetPay:", e)
        return JsonResponse({"error": True, "message": str(e)}, status=500)


@csrf_exempt
def init_cinetpay3(request):
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)

    try:
        data = json.loads(request.body)
        inscription_id = data.get("inscription_id")
        montant = data.get("montant")

        if not inscription_id or not montant:
            return JsonResponse({"error": "Champs requis manquants"}, status=400)

        print(f"→ Init paiement : inscription_id={inscription_id}, montant={montant}")

        inscription = Inscriptions.objects.get(pk=inscription_id)

        transaction_id = str(uuid.uuid4())

        return_url = "https://tonsite.com/cinetpay/return/"
        notify_url = "https://tonsite.com/cinetpay/notify/"

        result = init_cinetpay_payment(
            inscription=inscription,
            montant=montant,
            transaction_id=transaction_id,
            return_url=return_url,
            notify_url=notify_url
        )

        print("→ Réponse CinetPay : ", result)

        return JsonResponse({"url": result['data']['payment_url']})

    except Inscriptions.DoesNotExist:
        return JsonResponse({"error": "Inscription introuvable"}, status=404)

    except Exception as e:
        import traceback
        traceback.print_exc()  # ⛳ Très utile pour voir toute l’erreur dans la console
        return JsonResponse({"error": str(e)}, status=500)



@csrf_exempt
def init_cinetpayU(request):
    if request.method == "POST":
        data = json.loads(request.body)
        inscription_id = data.get("inscription_id")
        montant = data.get("montant")

        try:
            inscription = Inscriptions.objects.get(pk=inscription_id)
            transaction_id = str(uuid.uuid4())  # Génère un ID de transaction unique

            return_url = "https://tonsite.com/cinetpay/return/"
            notify_url = "https://tonsite.com/cinetpay/notify/"

            result = init_cinetpay_payment(
                inscription=inscription,
                montant=montant,
                transaction_id=transaction_id,
                return_url=return_url,
                notify_url=notify_url
            )

            return JsonResponse({"url": result['data']['payment_url']})

        except Inscriptions.DoesNotExist:
            return JsonResponse({"error": "Inscription introuvable"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from cinetpay_sdk.s_d_k import Cinetpay
from .models import Paiements  # Assurez-vous d'importer les bons modèles

@csrf_exempt
def cinetpay_notifyTO(request):
    if request.method == "POST":
        transaction_id = request.POST.get("transaction_id")
        client = Cinetpay(apikey="VOTRE_API_KEY", site_id="VOTRE_SITE_ID")
        result = client.TransactionVerfication_trx(transaction_id)

        if result.get('code') == '00':  # Paiement réussi
            # Récupérer le paiement localement selon transaction_id
            paiement = Paiements.objects.filter(transaction_id=transaction_id).first()
            if paiement and paiement.statut_validation == 'en_attente':
                paiement.statut_validation = 'valide'
                paiement.save()

        return HttpResponse("OK")


def ajouter_paiement_parentTO(request, inscription_id):
    inscription = get_object_or_404(Inscriptions, pk=inscription_id)
    total_du = inscription.montant_total_du()
    total_paye = inscription.montant_total_paye()
    solde = inscription.solde_restant()
    relances_actives = Relances.objects.filter(inscription=inscription, statut='active')

    montants_payes_par_relance = {
        relance.id: Paiements.objects.filter(
            inscription=inscription,
            echeance=relance.echeance,
            statut_validation='partiel'
        ).aggregate(total=Sum('montant'))['total'] or 0
        for relance in relances_actives
    }

    if request.method == 'POST':
        form = PaiementMultipleForm(request.POST, inscription=inscription)
        if form.is_valid():
            mode = form.cleaned_data['mode_paiement']
            paiements_temp = []
            montant_total_mobile = 0

            for relance, field_name in form.relance_fields:
                montant = form.cleaned_data.get(field_name)
                if montant and montant > 0:
                    montant_restant = relance.echeance_montant - montants_payes_par_relance.get(relance.id, 0)
                    statut_validation = 'valide' if montant >= montant_restant else ('partiel' if mode == 'especes' else 'en_attente')

                    paiement = Paiements(
                        inscription=inscription,
                        echeance=relance.echeance,
                        montant=montant,
                        date_paiement=timezone.now().date(),
                        mode_paiement=mode,
                        statut_validation=statut_validation,
                        valide_par=request.user if mode == 'especes' and statut_validation == 'valide' else None
                    )

                    paiements_temp.append((paiement, relance))
                    if mode == 'mobile_money':
                        montant_total_mobile += montant

            if mode == 'especes':
                for paiement, relance in paiements_temp:
                    paiement.save()
                    relance.total_verse = (relance.total_verse or 0) + paiement.montant
                    relance.total_solde = max(relance.echeance_montant - relance.total_verse, 0)
                    relance.save()
                return redirect('detail_paiement', eleve_id=inscription.eleve.id)

            elif mode == 'mobile_money':
                return_url = request.build_absolute_uri(reverse('detail_paiement', kwargs={'eleve_id': inscription.eleve.id}))
                notify_url = request.build_absolute_uri(reverse('cinetpay_notify'))

                result, transaction_id = init_cinetpay_payment(inscription, montant_total_mobile, return_url, notify_url)

                # Associer transaction_id aux paiements et sauvegarder en attente
                for paiement, _ in paiements_temp:
                    paiement.transaction_id = transaction_id
                    paiement.save()

                # Rediriger vers l’URL de paiement fournie par CinetPay
                return redirect(result.get('payment_url'))

    else:
        form = PaiementMultipleForm(inscription=inscription)

    return render(request, 'espace_parent/formulaire_paiement.html', {
        'form': form,
        'inscription': inscription,
        'total_du': total_du,
        'total_paye': total_paye,
        'solde': solde,
        'montants_payes': montants_payes_par_relance,
        'relances': relances_actives,
    })

    
# liste des paiements par etablissement ------------------------------------------------------------------------------------
@fonctionnalite_autorisee('liste_paiements_etablissement')   
def liste_paiements_etablissement(request):
    annee_active = AnneeScolaires.objects.get(active=True)
    etablissement = request.user.etablissement

    paiements = Paiements.objects.filter(
        inscription__annee_scolaire=annee_active,
        inscription__classe__etablissement=etablissement
    ).select_related('inscription__eleve', 'echeance')

    return render(request, 'frontoffice/paiements/liste.html', {
        'paiements': paiements,
        'annee_active': annee_active,
    })

@fonctionnalite_autorisee('liste_paiements_etablissement_transport')   
def liste_paiements_etablissement_transport(request):
    annee_active = AnneeScolaires.objects.get(active=True)
    etablissement = request.user.etablissement

    paiements = PaiementsTransports.objects.filter(
        inscription__annee_scolaire=annee_active,
        inscription__classe__etablissement=etablissement
    ).select_related('inscription__eleve', 'echeance')

    return render(request, 'frontoffice/paiements/liste_transport.html', {
        'paiements': paiements,
        'annee_active': annee_active,
    })

@fonctionnalite_autorisee('liste_paiements_etablissement_cantine')     
def liste_paiements_etablissement_cantine(request):
    annee_active = AnneeScolaires.objects.get(active=True)
    etablissement = request.user.etablissement

    paiements = PaiementsCantines.objects.filter(
        inscription__annee_scolaire=annee_active,
        inscription__classe__etablissement=etablissement
    ).select_related('inscription__eleve', 'echeance')

    return render(request, 'frontoffice/paiements/liste_cantine.html', {
        'paiements': paiements,
        'annee_active': annee_active,
    })
    
@fonctionnalite_autorisee('liste_paiements_arrieres_etablissement')   
def liste_paiements_arrieres_etablissement(request):
    annee_active = AnneeScolaires.objects.filter(active=False)
    etablissement = request.user.etablissement

    paiements = Paiements.objects.filter(
        inscription__annee_scolaire__in=annee_active,
        inscription__classe__etablissement=etablissement
    ).select_related('inscription__eleve', 'echeance')

    return render(request, 'frontoffice/paiements/liste_arrieres.html', {
        'paiements': paiements,
        'annee_active': annee_active,
    })

@fonctionnalite_autorisee('bilan_paiements_par_nature')  
def bilan_paiements_par_nature(request):
    annee_active = AnneeScolaires.objects.get(active=True)
    etablissement = request.user.etablissement

    # Tous les paiements de l'établissement cette année
    paiements = Paiements.objects.filter(
        inscription__annee_scolaire=annee_active,
        inscription__classe__etablissement=etablissement
    )

    # Bilan par nature (mode de paiement)
    bilan_par_mode = paiements.values('mode_paiement')\
        .annotate(total=Sum('montant'))\
        .order_by('mode_paiement')

    # Pour l'affichage avec les noms lisibles
    mode_labels = dict(Paiements.MODES)
    bilan_final = [
        {
            'mode': item['mode_paiement'],
            'libelle': mode_labels.get(item['mode_paiement'], item['mode_paiement']),
            'total': item['total'] or 0
        }
        for item in bilan_par_mode
    ]
    total_general = sum(item['total'] for item in bilan_final)

    return render(request, 'frontoffice/paiements/bilan_nature.html', {
        'bilan': bilan_final,
        'annee_active': annee_active,
        'total_general': total_general,
    })

@fonctionnalite_autorisee('bilan_paiements_par_nature_transport')     
def bilan_paiements_par_nature_transport(request):
    annee_active = AnneeScolaires.objects.get(active=True)
    etablissement = request.user.etablissement

    # Tous les paiements de l'établissement cette année
    paiements = PaiementsTransports.objects.filter(
        inscription__annee_scolaire=annee_active,
        inscription__classe__etablissement=etablissement
    )

    # Bilan par nature (mode de paiement)
    bilan_par_mode = paiements.values('mode_paiement')\
        .annotate(total=Sum('montant'))\
        .order_by('mode_paiement')

    # Pour l'affichage avec les noms lisibles
    mode_labels = dict(Paiements.MODES)
    bilan_final = [
        {
            'mode': item['mode_paiement'],
            'libelle': mode_labels.get(item['mode_paiement'], item['mode_paiement']),
            'total': item['total'] or 0
        }
        for item in bilan_par_mode
    ]
    total_general = sum(item['total'] for item in bilan_final)

    return render(request, 'frontoffice/paiements/bilan_nature_transport.html', {
        'bilan': bilan_final,
        'annee_active': annee_active,
        'total_general': total_general,
    })

@fonctionnalite_autorisee('bilan_paiements_par_nature_cantine')      
def bilan_paiements_par_nature_cantine(request):
    annee_active = AnneeScolaires.objects.get(active=True)
    etablissement = request.user.etablissement

    # Tous les paiements de l'établissement cette année
    paiements = PaiementsCantines.objects.filter(
        inscription__annee_scolaire=annee_active,
        inscription__classe__etablissement=etablissement
    )

    # Bilan par nature (mode de paiement)
    bilan_par_mode = paiements.values('mode_paiement')\
        .annotate(total=Sum('montant'))\
        .order_by('mode_paiement')

    # Pour l'affichage avec les noms lisibles
    mode_labels = dict(Paiements.MODES)
    bilan_final = [
        {
            'mode': item['mode_paiement'],
            'libelle': mode_labels.get(item['mode_paiement'], item['mode_paiement']),
            'total': item['total'] or 0
        }
        for item in bilan_par_mode
    ]
    total_general = sum(item['total'] for item in bilan_final)

    return render(request, 'frontoffice/paiements/bilan_nature_cantine.html', {
        'bilan': bilan_final,
        'annee_active': annee_active,
        'total_general': total_general,
    })
    

def liste_paiements_etablissement_back(request):
    annee_active = AnneeScolaires.objects.get(active=True)
    etablissement = request.user.etablissement

    paiements = Paiements.objects.filter(
        inscription__annee_scolaire=annee_active,
        inscription__classe__etablissement=etablissement
    ).select_related('inscription__eleve', 'echeance')

    return render(request, 'frontoffice/paiements/liste_paiements.html', {
        'paiements': paiements,
        'annee_active': annee_active,
    })

from django.http import HttpResponse
import xlwt

def export_paiements_excel(request):
    annee_active = AnneeScolaires.objects.get(active=True)
    etablissement = request.user.etablissement

    paiements = Paiements.objects.filter(
        inscription__annee_scolaire=annee_active,
        inscription__classe__etablissement=etablissement
    ).select_related('inscription__eleve', 'echeance')

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="paiements.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Paiements')

    # Entêtes
    columns = ['Élève', 'Montant', 'Mode de paiement', 'Statut', 'Date de paiement']
    for col_num, column_title in enumerate(columns):
        ws.write(0, col_num, column_title)

    # Données
    for row_num, paiement in enumerate(paiements, start=1):
        ws.write(row_num, 0, f"{paiement.inscription.eleve.nom} {paiement.inscription.eleve.prenoms}")
        ws.write(row_num, 1, paiement.montant)
        ws.write(row_num, 2, paiement.get_mode_paiement_display())
        ws.write(row_num, 3, paiement.get_statut_validation_display())
        ws.write(row_num, 4, paiement.date_paiement.strftime('%d/%m/%Y'))

    wb.save(response)
    return response

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def export_paiements_pdf(request):
    annee_active = AnneeScolaires.objects.get(active=True)
    etablissement = request.user.etablissement

    paiements = Paiements.objects.filter(
        inscription__annee_scolaire=annee_active,
        inscription__classe__etablissement=etablissement
    ).select_related('inscription__eleve', 'echeance')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="paiements.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 50, "Liste des Paiements")

    y = height - 80
    p.setFont("Helvetica", 10)
    p.drawString(30, y, "Élève")
    p.drawString(180, y, "Montant")
    p.drawString(250, y, "Mode")
    p.drawString(350, y, "Statut")
    p.drawString(450, y, "Date")

    y -= 20

    for paiement in paiements:
        if y < 50:
            p.showPage()
            y = height - 50

        p.drawString(30, y, f"{paiement.inscription.eleve.nom} {paiement.inscription.eleve.prenoms}")
        p.drawString(180, y, str(paiement.montant))
        p.drawString(250, y, paiement.get_mode_paiement_display())
        p.drawString(350, y, paiement.get_statut_validation_display())
        p.drawString(450, y, paiement.date_paiement.strftime('%d/%m/%Y'))
        y -= 20

    p.showPage()
    p.save()
    return response

def export_paiements_transport_excel(request):
    annee_active = AnneeScolaires.objects.get(active=True)
    etablissement = request.user.etablissement

    paiements = PaiementsTransports.objects.filter(
        inscription__annee_scolaire=annee_active,
        inscription__classe__etablissement=etablissement
    ).select_related('inscription__eleve', 'echeance')

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="paiements.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Paiements')

    # Entêtes
    columns = ['Élève', 'Montant', 'Mode de paiement', 'Statut', 'Date de paiement']
    for col_num, column_title in enumerate(columns):
        ws.write(0, col_num, column_title)

    # Données
    for row_num, paiement in enumerate(paiements, start=1):
        ws.write(row_num, 0, f"{paiement.inscription.eleve.nom} {paiement.inscription.eleve.prenoms}")
        ws.write(row_num, 1, paiement.montant)
        ws.write(row_num, 2, paiement.get_mode_paiement_display())
        ws.write(row_num, 3, paiement.get_statut_validation_display())
        ws.write(row_num, 4, paiement.date_paiement.strftime('%d/%m/%Y'))

    wb.save(response)
    return response

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def export_paiements_transport_pdf(request):
    annee_active = AnneeScolaires.objects.get(active=True)
    etablissement = request.user.etablissement

    paiements = PaiementsTransports.objects.filter(
        inscription__annee_scolaire=annee_active,
        inscription__classe__etablissement=etablissement
    ).select_related('inscription__eleve', 'echeance')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="paiements.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 50, "Liste des Paiements")

    y = height - 80
    p.setFont("Helvetica", 10)
    p.drawString(30, y, "Élève")
    p.drawString(180, y, "Montant")
    p.drawString(250, y, "Mode")
    p.drawString(350, y, "Statut")
    p.drawString(450, y, "Date")

    y -= 20

    for paiement in paiements:
        if y < 50:
            p.showPage()
            y = height - 50

        p.drawString(30, y, f"{paiement.inscription.eleve.nom} {paiement.inscription.eleve.prenoms}")
        p.drawString(180, y, str(paiement.montant))
        p.drawString(250, y, paiement.get_mode_paiement_display())
        p.drawString(350, y, paiement.get_statut_validation_display())
        p.drawString(450, y, paiement.date_paiement.strftime('%d/%m/%Y'))
        y -= 20

    p.showPage()
    p.save()
    return response

def export_paiements_cantine_excel(request):
    annee_active = AnneeScolaires.objects.get(active=True)
    etablissement = request.user.etablissement

    paiements = PaiementsCantines.objects.filter(
        inscription__annee_scolaire=annee_active,
        inscription__classe__etablissement=etablissement
    ).select_related('inscription__eleve', 'echeance')

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="paiements.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Paiements')

    # Entêtes
    columns = ['Élève', 'Montant', 'Mode de paiement', 'Statut', 'Date de paiement']
    for col_num, column_title in enumerate(columns):
        ws.write(0, col_num, column_title)

    # Données
    for row_num, paiement in enumerate(paiements, start=1):
        ws.write(row_num, 0, f"{paiement.inscription.eleve.nom} {paiement.inscription.eleve.prenoms}")
        ws.write(row_num, 1, paiement.montant)
        ws.write(row_num, 2, paiement.get_mode_paiement_display())
        ws.write(row_num, 3, paiement.get_statut_validation_display())
        ws.write(row_num, 4, paiement.date_paiement.strftime('%d/%m/%Y'))

    wb.save(response)
    return response

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def export_paiements_cantine_pdf(request):
    annee_active = AnneeScolaires.objects.get(active=True)
    etablissement = request.user.etablissement

    paiements = PaiementsCantines.objects.filter(
        inscription__annee_scolaire=annee_active,
        inscription__classe__etablissement=etablissement
    ).select_related('inscription__eleve', 'echeance')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="paiements.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 50, "Liste des Paiements")

    y = height - 80
    p.setFont("Helvetica", 10)
    p.drawString(30, y, "Élève")
    p.drawString(180, y, "Montant")
    p.drawString(250, y, "Mode")
    p.drawString(350, y, "Statut")
    p.drawString(450, y, "Date")

    y -= 20

    for paiement in paiements:
        if y < 50:
            p.showPage()
            y = height - 50

        p.drawString(30, y, f"{paiement.inscription.eleve.nom} {paiement.inscription.eleve.prenoms}")
        p.drawString(180, y, str(paiement.montant))
        p.drawString(250, y, paiement.get_mode_paiement_display())
        p.drawString(350, y, paiement.get_statut_validation_display())
        p.drawString(450, y, paiement.date_paiement.strftime('%d/%m/%Y'))
        y -= 20

    p.showPage()
    p.save()
    return response

def export_paiements_arrieres_excel(request):
    annee_active = AnneeScolaires.objects.filter(active=False)
    etablissement = request.user.etablissement

    paiements = PaiementsCantines.objects.filter(
        inscription__annee_scolaire__in=annee_active,
        inscription__classe__etablissement=etablissement
    ).select_related('inscription__eleve', 'echeance')

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="paiements.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Paiements')

    # Entêtes
    columns = ['Élève', 'Montant', 'Mode de paiement', 'Statut', 'Date de paiement']
    for col_num, column_title in enumerate(columns):
        ws.write(0, col_num, column_title)

    # Données
    for row_num, paiement in enumerate(paiements, start=1):
        ws.write(row_num, 0, f"{paiement.inscription.eleve.nom} {paiement.inscription.eleve.prenoms}")
        ws.write(row_num, 1, paiement.montant)
        ws.write(row_num, 2, paiement.get_mode_paiement_display())
        ws.write(row_num, 3, paiement.get_statut_validation_display())
        ws.write(row_num, 4, paiement.date_paiement.strftime('%d/%m/%Y'))

    wb.save(response)
    return response

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def export_paiements_arrieres_pdf(request):
    annee_active = AnneeScolaires.objects.filter(active=False)
    etablissement = request.user.etablissement

    paiements = PaiementsCantines.objects.filter(
        inscription__annee_scolaire__in=annee_active,
        inscription__classe__etablissement=etablissement
    ).select_related('inscription__eleve', 'echeance')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="paiements.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 50, "Liste des Paiements")

    y = height - 80
    p.setFont("Helvetica", 10)
    p.drawString(30, y, "Élève")
    p.drawString(180, y, "Montant")
    p.drawString(250, y, "Mode")
    p.drawString(350, y, "Statut")
    p.drawString(450, y, "Date")

    y -= 20

    for paiement in paiements:
        if y < 50:
            p.showPage()
            y = height - 50

        p.drawString(30, y, f"{paiement.inscription.eleve.nom} {paiement.inscription.eleve.prenoms}")
        p.drawString(180, y, str(paiement.montant))
        p.drawString(250, y, paiement.get_mode_paiement_display())
        p.drawString(350, y, paiement.get_statut_validation_display())
        p.drawString(450, y, paiement.date_paiement.strftime('%d/%m/%Y'))
        y -= 20

    p.showPage()
    p.save()
    return response

@fonctionnalite_autorisee('liste_echeances_groupes')   
def liste_echeances_groupes(request):
    annee_active = get_object_or_404(AnneeScolaires, active=True)
    etablissement = request.user.etablissement

    # Récupérer toutes les modalités pour cet établissement et cette année
    modalites = ModalitePaiements.objects.filter(etablissement=etablissement, annee_scolaire=annee_active)

    # Grouper les échéances par modalité
    echeances_groupes = {}
    for modalite in modalites:
        echeances = Echeances.objects.filter(modalite=modalite)
        echeances_groupes[modalite] = echeances

    return render(request, 'frontoffice/scolarites/echeances_groupes.html', {
        'echeances_groupes': echeances_groupes,
    })






# liste des paiements par back office ------------------------------------------------------------------------------------
@fonctionnalite_autorisee('liste_paiements_back')
def liste_paiements_back(request):
    annee_active = AnneeScolaires.objects.get(active=True)

    paiements = Paiements.objects.filter(
        inscription__annee_scolaire=annee_active
    ).select_related('inscription__eleve', 'echeance')

    return render(request, 'backoffice/paiements/liste.html', {
        'paiements': paiements,
        'annee_active': annee_active,
    })

@fonctionnalite_autorisee('liste_paiements_back_transport')
def liste_paiements_back_transport(request):
    annee_active = AnneeScolaires.objects.get(active=True)

    paiements = PaiementsTransports.objects.filter(
        inscription__annee_scolaire=annee_active
    ).select_related('inscription__eleve', 'echeance')

    return render(request, 'backoffice/paiements/liste_transport.html', {
        'paiements': paiements,
        'annee_active': annee_active,
    })
@fonctionnalite_autorisee('liste_paiements_back_cantine')    
def liste_paiements_back_cantine(request):
    annee_active = AnneeScolaires.objects.get(active=True)

    paiements = PaiementsCantines.objects.filter(
        inscription__annee_scolaire=annee_active
    ).select_related('inscription__eleve', 'echeance')

    return render(request, 'backoffice/paiements/liste_cantine.html', {
        'paiements': paiements,
        'annee_active': annee_active,
    })
    
@fonctionnalite_autorisee('liste_paiements_arrieres_back')    
def liste_paiements_arrieres_back(request):
    annee_active = AnneeScolaires.objects.filter(active=False)

    paiements = Paiements.objects.filter(
        inscription__annee_scolaire__in=annee_active
    ).select_related('inscription__eleve', 'echeance')

    return render(request, 'backoffice/paiements/liste_arrieres.html', {
        'paiements': paiements,
        'annee_active': annee_active,
    })


def bilan_paiements_par_nature_back(request):
    annee_active = AnneeScolaires.objects.get(active=True)

    # Tous les paiements de l'établissement cette année
    paiements = Paiements.objects.filter(
        inscription__annee_scolaire=annee_active
    )

    # Bilan par nature (mode de paiement)
    bilan_par_mode = paiements.values('mode_paiement')\
        .annotate(total=Sum('montant'))\
        .order_by('mode_paiement')

    # Pour l'affichage avec les noms lisibles
    mode_labels = dict(Paiements.MODES)
    bilan_final = [
        {
            'mode': item['mode_paiement'],
            'libelle': mode_labels.get(item['mode_paiement'], item['mode_paiement']),
            'total': item['total'] or 0
        }
        for item in bilan_par_mode
    ]
    total_general = sum(item['total'] for item in bilan_final)

    return render(request, 'backoffice/paiements/bilan_nature.html', {
        'bilan': bilan_final,
        'annee_active': annee_active,
        'total_general': total_general,
    })
    
def bilan_paiements_par_nature_transport_back(request):
    annee_active = AnneeScolaires.objects.get(active=True)

    # Tous les paiements de l'établissement cette année
    paiements = PaiementsTransports.objects.filter(
        inscription__annee_scolaire=annee_active
    )

    # Bilan par nature (mode de paiement)
    bilan_par_mode = paiements.values('mode_paiement')\
        .annotate(total=Sum('montant'))\
        .order_by('mode_paiement')

    # Pour l'affichage avec les noms lisibles
    mode_labels = dict(Paiements.MODES)
    bilan_final = [
        {
            'mode': item['mode_paiement'],
            'libelle': mode_labels.get(item['mode_paiement'], item['mode_paiement']),
            'total': item['total'] or 0
        }
        for item in bilan_par_mode
    ]
    total_general = sum(item['total'] for item in bilan_final)

    return render(request, 'backoffice/paiements/bilan_nature_transport.html', {
        'bilan': bilan_final,
        'annee_active': annee_active,
        'total_general': total_general,
    })
    
def bilan_paiements_par_nature_cantine_back(request):
    annee_active = AnneeScolaires.objects.get(active=True)

    # Tous les paiements de l'établissement cette année
    paiements = PaiementsCantines.objects.filter(
        inscription__annee_scolaire=annee_active
    )

    # Bilan par nature (mode de paiement)
    bilan_par_mode = paiements.values('mode_paiement')\
        .annotate(total=Sum('montant'))\
        .order_by('mode_paiement')

    # Pour l'affichage avec les noms lisibles
    mode_labels = dict(Paiements.MODES)
    bilan_final = [
        {
            'mode': item['mode_paiement'],
            'libelle': mode_labels.get(item['mode_paiement'], item['mode_paiement']),
            'total': item['total'] or 0
        }
        for item in bilan_par_mode
    ]
    total_general = sum(item['total'] for item in bilan_final)

    return render(request, 'backoffice/paiements/bilan_nature_cantine.html', {
        'bilan': bilan_final,
        'annee_active': annee_active,
        'total_general': total_general,
    })
    

def liste_paiements_etablissement_back(request):
    annee_active = AnneeScolaires.objects.get(active=True)

    paiements = Paiements.objects.filter(
        inscription__annee_scolaire=annee_active
    ).select_related('inscription__eleve', 'echeance')

    return render(request, 'backoffice/paiements/liste_paiements.html', {
        'paiements': paiements,
        'annee_active': annee_active,
    })

from django.http import HttpResponse
import xlwt

def export_paiements_excel_back(request):
    annee_active = AnneeScolaires.objects.get(active=True)

    paiements = Paiements.objects.filter(
        inscription__annee_scolaire=annee_active
    ).select_related('inscription__eleve', 'echeance')

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="paiements.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Paiements')

    # Entêtes
    columns = ['Élève', 'Montant', 'Mode de paiement', 'Statut', 'Date de paiement']
    for col_num, column_title in enumerate(columns):
        ws.write(0, col_num, column_title)

    # Données
    for row_num, paiement in enumerate(paiements, start=1):
        ws.write(row_num, 0, f"{paiement.inscription.classe.etablissement.nom}")
        ws.write(row_num, 1, f"{paiement.inscription.eleve.nom} {paiement.inscription.eleve.prenoms}")
        ws.write(row_num, 2, paiement.montant)
        ws.write(row_num, 3, paiement.get_mode_paiement_display())
        ws.write(row_num, 4, paiement.get_statut_validation_display())
        ws.write(row_num, 5, paiement.date_paiement.strftime('%d/%m/%Y'))

    wb.save(response)
    return response

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def export_paiements_pdf_back(request):
    annee_active = AnneeScolaires.objects.get(active=True)

    paiements = Paiements.objects.filter(
        inscription__annee_scolaire=annee_active
    ).select_related('inscription__eleve', 'inscription__classe__etablissement', 'echeance')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="paiements.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    def draw_title_and_headers(y_pos):
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, y_pos, "Liste des Paiements")

        y_pos -= 30
        p.setFont("Helvetica-Bold", 10)
        p.drawString(30, y_pos, "Établissement")
        p.drawString(120, y_pos, "Élève")
        p.drawString(250, y_pos, "Montant")
        p.drawString(310, y_pos, "Mode")
        p.drawString(380, y_pos, "Statut")
        p.drawString(450, y_pos, "Date")
        return y_pos - 15

    y = draw_title_and_headers(height - 50)

    p.setFont("Helvetica", 9)
    for paiement in paiements:
        if y < 60:
            p.showPage()
            y = draw_title_and_headers(height - 50)
            p.setFont("Helvetica", 9)

        p.drawString(30, y, paiement.inscription.classe.etablissement.nom[:20])
        p.drawString(120, y, f"{paiement.inscription.eleve.nom} {paiement.inscription.eleve.prenoms}"[:25])
        p.drawString(250, y, f"{paiement.montant:.0f}")
        p.drawString(310, y, paiement.get_mode_paiement_display())
        p.drawString(380, y, paiement.get_statut_validation_display())
        p.drawString(450, y, paiement.date_paiement.strftime('%d/%m/%Y'))
        y -= 15

    p.save()
    return response


def export_paiements_transport_excel_back(request):
    annee_active = AnneeScolaires.objects.get(active=True)

    paiements = PaiementsTransports.objects.filter(
        inscription__annee_scolaire=annee_active
    ).select_related('inscription__eleve', 'echeance')

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="paiements.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Paiements')

    # Entêtes
    columns = ['Établissement','Élève', 'Montant', 'Mode de paiement', 'Statut', 'Date de paiement']
    for col_num, column_title in enumerate(columns):
        ws.write(0, col_num, column_title)

    # Données
    for row_num, paiement in enumerate(paiements, start=1):
        ws.write(row_num, 0, f"{paiement.inscription.classe.etablissement.nom}")
        ws.write(row_num, 1, f"{paiement.inscription.eleve.nom} {paiement.inscription.eleve.prenoms}")
        ws.write(row_num, 2, paiement.montant)
        ws.write(row_num, 3, paiement.get_mode_paiement_display())
        ws.write(row_num, 4, paiement.get_statut_validation_display())
        ws.write(row_num, 5, paiement.date_paiement.strftime('%d/%m/%Y'))

    wb.save(response)
    return response

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def export_paiements_transport_pdf_back(request):
    annee_active = AnneeScolaires.objects.get(active=True)

    paiements = PaiementsTransports.objects.filter(
        inscription__annee_scolaire=annee_active
    ).select_related('inscription__eleve', 'echeance')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="paiements.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 50, "Liste des Paiements")

    y = height - 80
    p.setFont("Helvetica", 10)
    p.drawString(30, y, "Établissement")
    p.drawString(120, y, "Élève")
    p.drawString(250, y, "Montant")
    p.drawString(310, y, "Mode")
    p.drawString(380, y, "Statut")
    p.drawString(450, y, "Date")

    y -= 20

    for paiement in paiements:
        if y < 50:
            p.showPage()
            y = height - 50

        p.drawString(30, y, paiement.inscription.classe.etablissement.nom[:20])
        p.drawString(120, y, f"{paiement.inscription.eleve.nom} {paiement.inscription.eleve.prenoms}"[:25])
        p.drawString(250, y, f"{paiement.montant:.0f}")
        p.drawString(310, y, paiement.get_mode_paiement_display())
        p.drawString(380, y, paiement.get_statut_validation_display())
        p.drawString(450, y, paiement.date_paiement.strftime('%d/%m/%Y'))
        y -= 15

    p.showPage()
    p.save()
    return response

def export_paiements_cantine_excel_back(request):
    annee_active = AnneeScolaires.objects.get(active=True)

    paiements = PaiementsCantines.objects.filter(
        inscription__annee_scolaire=annee_active
    ).select_related('inscription__eleve', 'echeance')

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="paiements.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Paiements')

    # Entêtes
    columns = ['Établissement','Élève', 'Montant', 'Mode de paiement', 'Statut', 'Date de paiement']
    for col_num, column_title in enumerate(columns):
        ws.write(0, col_num, column_title)

    # Données
    for row_num, paiement in enumerate(paiements, start=1):
        ws.write(row_num, 0, f"{paiement.inscription.classe.etablissement.nom}")
        ws.write(row_num, 1, f"{paiement.inscription.eleve.nom} {paiement.inscription.eleve.prenoms}")
        ws.write(row_num, 2, paiement.montant)
        ws.write(row_num, 3, paiement.get_mode_paiement_display())
        ws.write(row_num, 4, paiement.get_statut_validation_display())
        ws.write(row_num, 5, paiement.date_paiement.strftime('%d/%m/%Y'))

    wb.save(response)
    return response

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def export_paiements_cantine_pdf_back(request):
    annee_active = AnneeScolaires.objects.get(active=True)

    paiements = PaiementsCantines.objects.filter(
        inscription__annee_scolaire=annee_active
    ).select_related('inscription__eleve', 'echeance')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="paiements.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 50, "Liste des Paiements")

    y = height - 80
    p.setFont("Helvetica", 10)
    p.drawString(30, y, "Établissement")
    p.drawString(120, y, "Élève")
    p.drawString(250, y, "Montant")
    p.drawString(310, y, "Mode")
    p.drawString(380, y, "Statut")
    p.drawString(450, y, "Date")

    y -= 20

    for paiement in paiements:
        if y < 50:
            p.showPage()
            y = height - 50

        p.drawString(30, y, paiement.inscription.classe.etablissement.nom[:20])
        p.drawString(120, y, f"{paiement.inscription.eleve.nom} {paiement.inscription.eleve.prenoms}"[:25])
        p.drawString(250, y, f"{paiement.montant:.0f}")
        p.drawString(310, y, paiement.get_mode_paiement_display())
        p.drawString(380, y, paiement.get_statut_validation_display())
        p.drawString(450, y, paiement.date_paiement.strftime('%d/%m/%Y'))
        y -= 15

    p.showPage()
    p.save()
    return response

def export_paiements_arrieres_excel_back(request):
    annee_active = AnneeScolaires.objects.filter(active=False)

    paiements = PaiementsCantines.objects.filter(
        inscription__annee_scolaire__in=annee_active
    ).select_related('inscription__eleve', 'echeance')

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="paiements.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Paiements')

    # Entêtes
    columns = ['Élève', 'Montant', 'Mode de paiement', 'Statut', 'Date de paiement']
    for col_num, column_title in enumerate(columns):
        ws.write(0, col_num, column_title)

    # Données
    for row_num, paiement in enumerate(paiements, start=1):
        ws.write(row_num, 0, f"{paiement.inscription.eleve.nom} {paiement.inscription.eleve.prenoms}")
        ws.write(row_num, 1, paiement.montant)
        ws.write(row_num, 2, paiement.get_mode_paiement_display())
        ws.write(row_num, 3, paiement.get_statut_validation_display())
        ws.write(row_num, 4, paiement.date_paiement.strftime('%d/%m/%Y'))

    wb.save(response)
    return response

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def export_paiements_arrieres_pdf_back(request):
    annee_active = AnneeScolaires.objects.filter(active=False)

    paiements = PaiementsCantines.objects.filter(
        inscription__annee_scolaire__in=annee_active
    ).select_related('inscription__eleve', 'echeance')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="paiements.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 50, "Liste des Paiements")

    y = height - 80
    p.setFont("Helvetica", 10)
    p.drawString(30, y, "Élève")
    p.drawString(180, y, "Montant")
    p.drawString(250, y, "Mode")
    p.drawString(350, y, "Statut")
    p.drawString(450, y, "Date")

    y -= 20

    for paiement in paiements:
        if y < 50:
            p.showPage()
            y = height - 50

        p.drawString(30, y, paiement.inscription.classe.etablissement.nom[:20])
        p.drawString(120, y, f"{paiement.inscription.eleve.nom} {paiement.inscription.eleve.prenoms}"[:25])
        p.drawString(250, y, f"{paiement.montant:.0f}")
        p.drawString(310, y, paiement.get_mode_paiement_display())
        p.drawString(380, y, paiement.get_statut_validation_display())
        p.drawString(450, y, paiement.date_paiement.strftime('%d/%m/%Y'))
        y -= 15

    p.showPage()
    p.save()
    return response



def liste_echeances_groupes_back(request):
    annee_active = get_object_or_404(AnneeScolaires, active=True)

    # Récupérer toutes les modalités pour cet établissement et cette année
    modalites = ModalitePaiements.objects.filter(annee_scolaire=annee_active)

    # Grouper les échéances par modalité
    echeances_groupes = {}
    for modalite in modalites:
        echeances = Echeances.objects.filter(modalite=modalite)
        echeances_groupes[modalite] = echeances

    return render(request, 'backoffice/scolarites/echeances_groupes.html', {
        'echeances_groupes': echeances_groupes,
    })










#   ==================================================================      TEST      ==============================================================================
# ============================================================================ TEST BON ===========================================================================   
# ============================================================================ TEST BON =========================================================================== 
# ============================================================================ TEST BON =========================================================================== 
# ============================================================================ TEST BON ===========================================================================

def ajouter_paiement1(request, inscription_id):
    inscription = get_object_or_404(Inscriptions, id=inscription_id)

    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            paiement = form.save(commit=False)
            paiement.inscription = inscription
            paiement.utilisateur = request.user
            paiement.save()
            return redirect('detail_inscription', inscription_id=inscription.id)
    else:
        form = PaiementForm()

    return render(request, 'paiements/ajouter_paiement.html', {
        'form': form,
        'inscription': inscription,
    })
    
from django.shortcuts import render, redirect, get_object_or_404
from scolarites.models import Paiements
from eleves.models import Inscriptions
from django.utils import timezone
from .forms import PaiementMultipleForm

def ajouter_paiementOK(request, inscription_id):
    inscription = get_object_or_404(Inscriptions, pk=inscription_id)

    total_du = inscription.montant_total_du()
    total_paye = inscription.montant_total_paye()
    solde = inscription.solde_restant()

    if request.method == 'POST':
        form = PaiementMultipleForm(request.POST, inscription=inscription)
        if form.is_valid():
            mode = form.cleaned_data['mode_paiement']
            for echeance, field_name in form.echeance_fields:
                montant = form.cleaned_data.get(field_name)
                if montant and montant > 0:
                    Paiements.objects.create(
                        inscription=inscription,
                        echeance=echeance,
                        montant=montant,
                        date_paiement=timezone.now().date(),
                        mode_paiement=mode,
                        statut_validation='valide' if mode == 'especes' else 'en_attente',
                        valide_par=request.user if mode == 'especes' else None
                    )
            #return redirect('detail_inscription', inscription_id=inscription.id)
            return redirect('detail_paiement', eleve_id=inscription.eleve.id)
    else:
        form = PaiementMultipleForm(inscription=inscription)

    return render(request, 'frontoffice/paiements/formulaire_paiement.html', {
        'form': form,
        'inscription': inscription,
        'total_du': total_du,
        'total_paye': total_paye,
        'solde': solde,
    })

from django.utils import timezone
from django.db.models import Sum

def ajouter_paiementOK2(request, inscription_id):
    inscription = get_object_or_404(Inscriptions, pk=inscription_id)

    total_du = inscription.montant_total_du()
    total_paye = inscription.montant_total_paye()
    solde = inscription.solde_restant()

    if request.method == 'POST':
        form = PaiementMultipleForm(request.POST, inscription=inscription)
        if form.is_valid():
            mode = form.cleaned_data['mode_paiement']
            for echeance, field_name in form.echeance_fields:
                montant = form.cleaned_data.get(field_name)
                if montant and montant > 0:
                    # Total déjà payé pour cette échéance
                    total_paye_echeance = Paiements.objects.filter(
                        inscription=inscription,
                        echeance=echeance,
                        statut_validation='valide'
                    ).aggregate(total=Sum('montant'))['total'] or 0
                    

                    montant_restant = echeance.montant - total_paye_echeance

                    # Déterminer le statut de validation
                    if montant >= montant_restant:
                        statut_validation = 'valide'
                    else:
                        statut_validation = 'partiel' if mode == 'especes' else 'en_attente'

                    Paiements.objects.create(
                        inscription=inscription,
                        echeance=echeance,
                        montant=montant,
                        date_paiement=timezone.now().date(),
                        mode_paiement=mode,
                        statut_validation=statut_validation,
                        valide_par=request.user if mode == 'especes' and statut_validation == 'valide' else None
                    )

            return redirect('detail_paiement', eleve_id=inscription.eleve.id)
    else:
        form = PaiementMultipleForm(inscription=inscription)

    return render(request, 'frontoffice/paiements/formulaire_paiement.html', {
        'form': form,
        'inscription': inscription,
        'total_du': total_du,
        'total_paye': total_paye,
        'solde': solde,
    })
    

def modifier_echeances_modaliteA(request, modalite_id):
    modalite = get_object_or_404(ModalitePaiements, id=modalite_id)
    EcheanceFormSet = modelformset_factory(Echeances, form=EcheanceForm, extra=0)

    queryset = Echeances.objects.filter(modalite=modalite)
    formset = EcheanceFormSet(queryset=queryset)

    if request.method == 'POST':
        formset = EcheanceFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            formset.save()
            return redirect('afficher_niveaux_et_modalites', etablissement_id=modalite.etablissement.id)

    return render(request, 'backoffice/scolarites/echeances/modifier_echeances.html', {
        'modalite': modalite,
        'formset': formset
    })
    
# ============================================================================ TEST BON ===========================================================================   
# ============================================================================ TEST BON =========================================================================== 
# ============================================================================ TEST BON =========================================================================== 
# ============================================================================ TEST BON ===========================================================================