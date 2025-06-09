# forms.py
from django import forms

from cores.models import AnneeScolaires
from etablissements.models import Classes
from .models import Eleves, Inscriptions, LienParente, Parents

class ImportElevesForm(forms.Form):
    fichier_excel = forms.FileField(label="Fichier Excel (.xlsx)")
    
class EleveForm(forms.ModelForm):
    class Meta:
        model = Eleves
        fields = ['matricule','nom', 'prenoms', 'sexe', 'date_naissance', 'lieu_naissance', 'parent']
        widgets = {
            'matricule': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Laisser vide pour générer automatiquement'}),
            'nom': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Nom'}),
            'prenoms': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Prénoms'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control','placeholder': 'lieu_naissance'}),
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control','type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['matricule'].required = False

 

LienParenteFormSet = forms.inlineformset_factory(
    Eleves,
    LienParente,
    fields=('parent', 'lien'),
    extra=1,
    can_delete=True
)

class LienParenteForm(forms.ModelForm):
    class Meta:
        model = LienParente
        fields = ['eleve', 'parent', 'lien']
        widgets = {
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'lien': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ex : Père, Mère, Tuteur, ...'})
        }


class ParentForm(forms.ModelForm):
    class Meta:
        model = Parents
        fields = ['nom_complet', 'telephone', 'email']
        widgets = {
            'nom_complet': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Nom et prénoms'}),
            'telephone': forms.DateInput(attrs={'class': 'form-control','placeholder': 'Ex : 0000000000'}),
            'email': forms.DateInput(attrs={'class': 'form-control','placeholder': 'Ex : email@gmail.com'}),
        }



class FormulaireInscriptionOK(forms.ModelForm):
    class Meta:
        model = Inscriptions
        fields = ['classe', 'statut']
        widgets = {
            'classe': forms.Select(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(FormulaireInscriptionOK, self).__init__(*args, **kwargs)
        self.fields['classe'].queryset = Classes.objects.all()



class FormulaireInscriptionprimaire(forms.ModelForm):
    class Meta:
        model = Inscriptions
        fields = ['classe', 'transport','cantine','reduction']
        widgets = {
            'classe': forms.Select(attrs={'class': 'form-control'}),
            'transport': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cantine': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reduction': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant FCFA'}),
        } 

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # On récupère l'utilisateur passé depuis la vue
        super(FormulaireInscriptionprimaire, self).__init__(*args, **kwargs)

        if user:
            # Récupérer l'établissement de l'utilisateur connecté
            etablissement = self.get_etablissement_utilisateur(user)

            # Récupérer l'année scolaire active
            annee_active = AnneeScolaires.objects.filter(active=True).first()

            # Filtrer les classes de l'établissement et de l'année scolaire active
            if etablissement and annee_active:
                self.fields['classe'].queryset = Classes.objects.filter(
                    etablissement=etablissement,
                    annee_scolaire=annee_active
                )

    def get_etablissement_utilisateur(self, user):
        # Utiliser l'utilisateur passé pour récupérer l'établissement
        return getattr(user, 'etablissement', None)


class FormulaireInscription(forms.ModelForm):
    class Meta:
        model = Inscriptions
        fields = ['classe', 'statut','transport','cantine','reduction']
        widgets = {
            'classe': forms.Select(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'transport': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cantine': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reduction': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant FCFA'}),
        } 

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # On récupère l'utilisateur passé depuis la vue
        super(FormulaireInscription, self).__init__(*args, **kwargs)

        if user:
            # Récupérer l'établissement de l'utilisateur connecté
            etablissement = self.get_etablissement_utilisateur(user)

            # Récupérer l'année scolaire active
            annee_active = AnneeScolaires.objects.filter(active=True).first()

            # Filtrer les classes de l'établissement et de l'année scolaire active
            if etablissement and annee_active:
                self.fields['classe'].queryset = Classes.objects.filter(
                    etablissement=etablissement,
                    annee_scolaire=annee_active
                )

    def get_etablissement_utilisateur(self, user):
        # Utiliser l'utilisateur passé pour récupérer l'établissement
        return getattr(user, 'etablissement', None)