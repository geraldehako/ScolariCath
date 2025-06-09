from datetime import timezone
from django import forms

from cores.models import AnneeScolaires
from eleves.models import Relances
from etablissements.models import Niveaux
from .models import Echeances, ModaliteCantines, ModalitePaiements, ModaliteTransports, Mois, Paiements, PaiementsCantines, PaiementsTransports

class MoisForm(forms.ModelForm):
    class Meta:
        model = Mois
        fields = ['mois']
        widgets = {
            'mois': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex : Septembre'})
        }
        
class ModalitePaiementsForm(forms.ModelForm):
    class Meta:
        model = ModalitePaiements
        fields = '__all__'

class ModaliteCantineForm(forms.ModelForm):
    class Meta:
        model = ModaliteCantines
        fields = ['nom', 'mois', 'montant']
        widgets = {
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'mois': forms.Select(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de modalité'}),
        }

class ModaliteTransportForm(forms.ModelForm):
    class Meta:
        model = ModaliteTransports
        fields = ['nom', 'mois', 'montant']
        widgets = {
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'mois': forms.Select(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de modalité'}),
        }

class EcheancesForm(forms.ModelForm):
    class Meta:
        model = Echeances
        fields = '__all__'
        widgets = {
            'date_limite': forms.DateInput(attrs={'type': 'date'}),
        }


class ModalitePaiementForm(forms.ModelForm):
    class Meta:
        model = ModalitePaiements
        fields = ['nom', 'montant',  'nombre_echeances', 'applicable_aux_non_affectes']  #'niveau',
        widgets = {
            #'niveau': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'nombre_echeances': forms.NumberInput(attrs={'class': 'form-control'}),
            'mode_paiement': forms.Select(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de modalité'}),
        }

    def __init__(self, *args, **kwargs):
        etablissement = kwargs.pop('etablissement', None)
        super().__init__(*args, **kwargs)

        if etablissement:
            cycles = etablissement.types.all()  # récupérer les cycles liés à l'établissement
            self.fields['niveau'].queryset = Niveaux.objects.filter(cycle__in=cycles)
            self.fields['etablissement'].initial = etablissement
            self.fields['etablissement'].disabled = True
            
    def clean(self):
        cleaned_data = super().clean()
        niveau = cleaned_data.get('niveau')
        etablissement = cleaned_data.get('etablissement')
        annee_scolaire = AnneeScolaires.objects.filter(active=True).first()

        if niveau and etablissement:
            if ModalitePaiements.objects.filter(
                etablissement=etablissement,
                annee_scolaire=annee_scolaire,
                niveau=niveau
            ).exists():
                raise forms.ValidationError("Une modalité de paiement existe déjà pour ce niveau et cette année.")
        return cleaned_data




class EcheanceForm(forms.ModelForm):
    class Meta:
        model = Echeances
        fields = ['nom', 'montant', 'date_limite']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de modalité'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_limite': forms.DateInput(attrs={'type': 'date','class': 'form-control'}),
        }


class PaiementEleveForm(forms.Form):
    modalite = forms.ModelChoiceField(
        queryset=ModalitePaiements.objects.none(),
        label="Modalité de paiement"
    )

    def __init__(self, *args, **kwargs):
        eleve = kwargs.pop('eleve', None)
        super().__init__(*args, **kwargs)

        if eleve:
            self.fields['modalite'].queryset = ModalitePaiements.objects.filter(
                niveau=eleve.niveau,
                etablissement=eleve.etablissement,
                annee_scolaire=eleve.annee_scolaire,
                applicable_aux_non_affectes=not eleve.est_affecte
            )


class FormulairePaiement(forms.ModelForm):
    class Meta:
        model = Paiements
        fields = ['echeance', 'montant', 'mode_paiement']
        widgets = {
            'echeance': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'mode_paiement': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(FormulairePaiement, self).__init__(*args, **kwargs)
        self.fields['echeance'].queryset = self.fields['echeance'].queryset.none()  # sera défini dynamiquement

#  Formulaire de paiement apres inscription =====================================================================================================
class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiements
        fields = ['echeance', 'montant']
        widgets = {
            'echeance': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tu peux filtrer les échéances ici si nécessaire


from django import forms
from scolarites.models import Paiements
from django.utils.safestring import mark_safe
from django.db.models import Sum
from django import forms
from scolarites.models import Paiements
from django.utils.safestring import mark_safe
from django.db.models import Sum

class PaiementMultipleFormOK(forms.Form):
    mode_paiement = forms.ChoiceField(choices=Paiements.MODES, widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, inscription=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.inscription = inscription
        self.echeance_fields = []
        

        if inscription:
            for echeance in inscription.echeances_non_soldees():
                total_paye = Paiements.objects.filter(
                    inscription=inscription,
                    echeance=echeance,
                    statut_validation='valide'
                ).aggregate(total=Sum('montant'))['total'] or 0

                montant_restant = echeance.montant - total_paye

                field_name = f"echeance_{echeance.id}"
                
                readonly = montant_restant <= 0
                
                self.fields[field_name] = forms.IntegerField(
                    required=False,
                    #min_value=0,
                    #max_value=montant_restant,
                    #label=mark_safe(f"{echeance.nom} — Montant restant : {montant_restant} FCFA"),
                    #widget=forms.NumberInput(attrs={
                    #    'class': 'form-control',
                    #    'readonly': montant_restant == 0,
                    #    'style': 'background-color: #eee;' if montant_restant == 0 else ''
                    #})
                    min_value=0,
                    max_value=max(0, montant_restant),  # pour éviter max_value négatif
                    label=mark_safe(f"{echeance.nom} — Montant restant : {montant_restant} FCFA"),
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control',
                        'readonly': readonly,
                        'style': 'background-color: #eee;' if readonly else ''
                    })
                )
                self.echeance_fields.append((echeance, field_name))

from django import forms
from django.utils.safestring import mark_safe
from django.db.models import Sum
from .models import Paiements  # Assure-toi que le modèle est bien importé

class PaiementMultipleFormBONJEUDI(forms.Form):
    mode_paiement = forms.ChoiceField(
        choices=Paiements.MODES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Mode de paiement"
    )

    def __init__(self, *args, inscription=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.inscription = inscription
        self.echeance_fields = []

        if inscription:
            for echeance in inscription.echeances_non_soldees():
                # Total déjà payé pour cette échéance
                total_paye = Paiements.objects.filter(
                    inscription=inscription,
                    echeance=echeance,
                    statut_validation='partiel'
                ).aggregate(total=Sum('montant'))['total'] or 0

                montant_restant = echeance.montant - total_paye
                montant_restant = max(0, montant_restant)  # sécurité

                field_name = f"echeance_{echeance.id}"
                is_solde = montant_restant == 0

                self.fields[field_name] = forms.IntegerField(
                    required=False,
                    min_value=0,
                    max_value=montant_restant,
                    label=mark_safe(
                        f"<strong>{echeance.nom}</strong><br>"
                        f"Montant échéance : {echeance.montant} FCFA<br>"
                        f"Déjà payé : {total_paye} FCFA<br>"
                        f"<strong>Restant :</strong> {montant_restant} FCFA"
                    ),
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control',
                        'readonly': is_solde,
                        'style': 'background-color: #eee;' if is_solde else ''
                    })
                )

                self.echeance_fields.append((echeance, field_name))


from django import forms
from django.utils.safestring import mark_safe
from django.db.models import Sum
from .models import Paiements

class PaiementMultipleForm(forms.Form):
    mode_paiement = forms.ChoiceField(
        choices=Paiements.MODES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Mode de paiement"
    )
    numero_transaction = forms.CharField(
        required=False,
        label="Numéro de transaction",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    justificatif = forms.FileField(
        required=False,
        label="Justificatif (optionnel)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, inscription=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.inscription = inscription
        self.relance_fields = []

        if inscription:
            relances = Relances.objects.filter(inscription=inscription, statut='active')
            for relance in relances:
                total_paye = Paiements.objects.filter(
                    inscription=inscription,
                    echeance=relance.echeance,
                    statut_validation='partiel'
                ).aggregate(total=Sum('montant'))['total'] or 0

                montant_restant = (relance.echeance_montant or 0) - total_paye
                montant_restant = max(0, montant_restant)

                field_name = f"relance_{relance.id}"
                is_solde = montant_restant == 0

                self.fields[field_name] = forms.IntegerField(
                    required=False,
                    min_value=0,
                    max_value=montant_restant,
                    label=mark_safe(
                        f"<strong>{relance.echeance.nom}</strong><br>"
                        f"Montant échéance : {relance.echeance_montant} FCFA<br>"
                        f"Déjà payé : {total_paye} FCFA<br>"
                        f"<strong>Restant :</strong> {montant_restant} FCFA"
                    ),
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control',
                        'readonly': is_solde,
                        'style': 'background-color: #eee;' if is_solde else ''
                    })
                )

                self.relance_fields.append((relance, field_name))
                
    def clean_numero_transaction(self):
        numero = self.cleaned_data.get('numero_transaction')
        mode = self.cleaned_data.get('mode_paiement')

        if mode == 'virement':
            if not numero:
                raise forms.ValidationError("Le numéro de transaction est requis pour un virement.")
            if Paiements.objects.filter(numero_transaction=numero).exists():
                raise forms.ValidationError("Ce numéro de transaction est déjà utilisé.")
        return numero



from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import PaiementsCantines

class PaiementCantineFormBon(forms.ModelForm):
    relance_fields = []

    class Meta:
        model = PaiementsCantines
        fields = ['mode_paiement', 'numero_transaction', 'justificatif']
        widgets = {
            'mode_paiement': forms.Select(attrs={'class': 'form-control'}),
            'numero_transaction': forms.TextInput(attrs={'class': 'form-control'}),
            'justificatif': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.inscription = kwargs.pop('inscription')
        self.modalites = kwargs.pop('modalites')
        super().__init__(*args, **kwargs)

        self.relance_fields = []

        for modalite in self.modalites:
            field_name = f"echeance_{modalite.id}"
            montant_max = modalite.montant
            self.fields[field_name] = forms.IntegerField(
                required=False,
                min_value=0,
                label=f"{modalite.nom} – {modalite.montant} FCFA",
                widget=forms.NumberInput(attrs={'class': 'form-control','max': montant_max})
            )
            self.relance_fields.append((modalite, field_name))
    
    def clean(self):
        cleaned_data = super().clean()
        montant_total = 0

        for modalite, field_name in self.relance_fields:
            montant = cleaned_data.get(field_name)
            if montant:
                montant_total += montant

        if montant_total == 0:
            raise forms.ValidationError("Veuillez saisir au moins un montant supérieur à 0.")

        return cleaned_data

    def clean_numero_transaction(self):
        numero = self.cleaned_data.get('numero_transaction')
        if numero:
            qs = PaiementsCantines.objects.filter(numero_transaction=numero)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ce numéro de transaction est déjà utilisé.")
        return numero

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        paiements = []

        for modalite, field_name in self.relance_fields:
            montant = cleaned_data.get(field_name)
            if montant and montant > 0:
                paiement = PaiementsCantines(
                    inscription=self.inscription,
                    echeance=modalite,
                    montant=montant,
                    date_paiement=timezone.now(),
                    mode_paiement=cleaned_data['mode_paiement'],
                    numero_transaction=cleaned_data.get('numero_transaction'),
                    justificatif=cleaned_data.get('justificatif'),
                )
                paiements.append(paiement)

        for p in paiements:
            p.save()

        return paiements

from django import forms

class PaiementCantineForm(forms.ModelForm):
    relance_fields = []

    class Meta:
        model = PaiementsCantines
        fields = ['mode_paiement', 'numero_transaction', 'justificatif']
        widgets = {
            'mode_paiement': forms.Select(attrs={'class': 'form-control'}),
            'numero_transaction': forms.TextInput(attrs={'class': 'form-control'}),
            'justificatif': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.inscription = kwargs.pop('inscription')
        self.modalites = kwargs.pop('modalites')  # Liste des échéances non payées
        super().__init__(*args, **kwargs)

        self.relance_fields = []

        for modalite in self.modalites:
            field_name = f"echeance_{modalite.id}"
            self.fields[field_name] = forms.BooleanField(
                required=False,
                label=f"{modalite.mois} – {modalite.nom} – {modalite.montant} FCFA",
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
            )
            self.relance_fields.append((modalite, field_name))

    def clean(self):
        cleaned_data = super().clean()
        selection = [
            modalite for modalite, field_name in self.relance_fields
            if cleaned_data.get(field_name)
        ]

        if not selection:
            raise forms.ValidationError("Veuillez sélectionner au moins une modalité à payer.")

        return cleaned_data

    def clean_numero_transaction(self):
        numero = self.cleaned_data.get('numero_transaction')
        if numero:
            qs = PaiementsCantines.objects.filter(numero_transaction=numero)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ce numéro de transaction est déjà utilisé.")
        return numero

    def save(self, commit=True, user=None):
        cleaned_data = self.cleaned_data
        paiements = []

        for modalite, field_name in self.relance_fields:
            if cleaned_data.get(field_name):  # Si l'échéance a été cochée
                paiement = PaiementsCantines(
                    inscription=self.inscription,
                    echeance=modalite,
                    montant=modalite.montant,
                    date_paiement=timezone.now(),
                    mode_paiement=cleaned_data['mode_paiement'],
                    numero_transaction=cleaned_data.get('numero_transaction'),
                    statut_validation='valide',
                    justificatif=cleaned_data.get('justificatif'),
                )
                if user:
                    paiement.valide_par = user
                paiements.append(paiement)

        for paiement in paiements:
            paiement.save()

        return paiements

class PaiementTransportForm(forms.ModelForm):
    relance_fields = []

    class Meta:
        model = PaiementsTransports
        fields = ['mode_paiement', 'numero_transaction', 'justificatif']
        widgets = {
            'mode_paiement': forms.Select(attrs={'class': 'form-control'}),
            'numero_transaction': forms.TextInput(attrs={'class': 'form-control'}),
            'justificatif': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.inscription = kwargs.pop('inscription')
        self.modalites = kwargs.pop('modalites')  # Liste des échéances non payées
        super().__init__(*args, **kwargs)

        self.relance_fields = []

        for modalite in self.modalites:
            field_name = f"echeance_{modalite.id}"
            self.fields[field_name] = forms.BooleanField(
                required=False,
                label=f"{modalite.mois} – {modalite.nom} – {modalite.montant} FCFA",
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
            )
            self.relance_fields.append((modalite, field_name))

    def clean(self):
        cleaned_data = super().clean()
        selection = [
            modalite for modalite, field_name in self.relance_fields
            if cleaned_data.get(field_name)
        ]

        if not selection:
            raise forms.ValidationError("Veuillez sélectionner au moins une modalité à payer.")

        return cleaned_data

    def clean_numero_transaction(self):
        numero = self.cleaned_data.get('numero_transaction')
        if numero:
            qs = PaiementsTransports.objects.filter(numero_transaction=numero)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ce numéro de transaction est déjà utilisé.")
        return numero

    def save(self, commit=True, user=None):
        cleaned_data = self.cleaned_data
        paiements = []

        for modalite, field_name in self.relance_fields:
            if cleaned_data.get(field_name):  # Si l'échéance a été cochée
                paiement = PaiementsTransports(
                    inscription=self.inscription,
                    echeance=modalite,
                    montant=modalite.montant,
                    date_paiement=timezone.now(),
                    mode_paiement=cleaned_data['mode_paiement'],
                    numero_transaction=cleaned_data.get('numero_transaction'),
                    statut_validation='valide',
                    justificatif=cleaned_data.get('justificatif'),
                )
                if user:
                    paiement.valide_par = user
                paiements.append(paiement)

        for paiement in paiements:
            paiement.save()

        return paiements