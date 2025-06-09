from django import forms

from authentifications.models import Roles, Utilisateurs
from enseignants.models import Enseignants, TenueDeClasse
from matieres.models import Matieres
from .models import Etablissements, Niveaux, Classes, EmploiTemps, TypeEtablissement

class TypeEtablissementForm(forms.ModelForm):
    class Meta:
        model = TypeEtablissement
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex : Collège'})
        }
         
class EtablissementForm(forms.ModelForm):
    class Meta:
        model = Etablissements
        fields = ['nom', 'types', 'adresse', 'localisation', 'code_etablissement', 'directeur', 'logo']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l’établissement'}),
            'types': forms.CheckboxSelectMultiple(),  # 👈 à utiliser uniquement si `types` est un ManyToManyField
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'localisation': forms.TextInput(attrs={'class': 'form-control'}),
            'code_etablissement': forms.TextInput(attrs={'class': 'form-control'}),
            'directeur': forms.Select(attrs={'class': 'form-select'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}), 
        }
            
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        roles = Roles.objects.filter(nom='Direction')  # plusieurs rôles possibles
        self.fields['directeur'].queryset = Utilisateurs.objects.filter(role__in=roles)
        self.fields['directeur'].required = False


class NiveauForm(forms.ModelForm):
    class Meta:
        model = Niveaux
        fields = '__all__'
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du niveau'}),
            'cycle': forms.Select(attrs={'class': 'form-select'}),
        }

class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classes
        fields = ['nom', 'niveau', 'etablissement', 'capacite']  # corrigé ici
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'capacite': forms.NumberInput(attrs={'class': 'form-control'}), 
        }
    

class ClasseEtForm(forms.ModelForm):
    class Meta:
        model = Classes
        fields = ['nom', 'niveau', 'etablissement', 'capacite']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'capacite': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        etablissement = kwargs.pop('etablissement', None)
        super().__init__(*args, **kwargs)

        if etablissement:
            cycles = etablissement.types.all()  # récupérer les cycles liés à l'établissement
            self.fields['niveau'].queryset = Niveaux.objects.filter(cycle__in=cycles)
            self.fields['etablissement'].initial = etablissement
            self.fields['etablissement'].disabled = True



class EmploiTempsFormUn(forms.ModelForm):
    class Meta:
        model = EmploiTemps
        fields = '__all__'
        widgets = {
            'jour': forms.Select(attrs={'class': 'form-select'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'professeur': forms.Select(attrs={'class': 'form-select'}),
        }


class EmploiTempsForm(forms.ModelForm):
    class Meta:
        model = EmploiTemps
        fields = '__all__'
        widgets = {
            'jour': forms.Select(attrs={'class': 'form-select'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'professeur': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        initial_classe = kwargs.get('initial', {}).get('classe')
        data_classe = kwargs.get('data', {}).get('classe')

        super().__init__(*args, **kwargs)

        classe_obj = None
        if isinstance(initial_classe, Classes):
            classe_obj = initial_classe
        elif data_classe:
            try:
                classe_obj = Classes.objects.get(pk=data_classe)
            except Classes.DoesNotExist:
                pass

        if classe_obj:
            self.fields['matiere'].queryset = Matieres.objects.filter(niveau=classe_obj.niveau)
        else:
            self.fields['matiere'].queryset = Matieres.objects.none()

        # Préremplir les professeurs selon la matière sélectionnée
        matiere = None
        if self.instance and self.instance.pk:
            matiere = self.instance.matiere
        elif 'matiere' in self.data:
            try:
                matiere_id = int(self.data.get('matiere'))
                matiere = Matieres.objects.get(id=matiere_id)
            except (ValueError, Matieres.DoesNotExist):
                pass

        if matiere:
            self.fields['professeur'].queryset = Enseignants.objects.filter(specialite__icontains=matiere.nom)
        else:
            self.fields['professeur'].queryset = Enseignants.objects.none()


# EmploiTempsPrimaireForm.py

class EmploiTempsPrimaireForm(forms.ModelForm):
    class Meta:
        model = EmploiTemps
        fields = ['jour', 'heure_debut', 'heure_fin', 'matiere', 'tennant']
        widgets = {
            'jour': forms.Select(attrs={'class': 'form-select'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'tennant': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        initial_classe = kwargs.get('initial', {}).get('classe')
        data_classe = kwargs.get('data', {}).get('classe')

        super().__init__(*args, **kwargs)

        classe_obj = None
        if isinstance(initial_classe, Classes):
            classe_obj = initial_classe
        elif data_classe:
            try:
                classe_obj = Classes.objects.get(pk=data_classe)
            except Classes.DoesNotExist:
                pass

        if classe_obj:
            self.fields['matiere'].queryset = Matieres.objects.filter(niveau=classe_obj.niveau)
            self.fields['tennant'].queryset = TenueDeClasse.objects.filter(classe=classe_obj)
        else:
            self.fields['matiere'].queryset = Matieres.objects.none()
            self.fields['tennant'].queryset = TenueDeClasse.objects.none()
