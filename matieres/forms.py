from django import forms
from .models import Matieres, CoefficientMatieres, CoefficientMatieresEtablissements, CoefficientMatiereParPeriode 

class MatiereForm(forms.ModelForm):
    class Meta:
        model = Matieres
        fields = '__all__'
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'cycle': forms.Select(attrs={'class': 'form-select'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'obligatoire': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
class MatiereEtForm(forms.ModelForm):
    class Meta:
        model = Matieres
        fields = ['nom']  # pas le champ cycle ici, il est injecté dans la vue
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}) }
        
class CoefficientMatiereForm1(forms.ModelForm):
    class Meta:
        model = CoefficientMatieres
        fields = '__all__'
        widgets = {
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CoefficientMatiereForm(forms.ModelForm):
    class Meta:
        model = CoefficientMatieres
        fields = ['niveau', 'coefficient']
        widgets = {
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CoefficientMatiereEtablissementForm(forms.ModelForm):
    class Meta:
        model = CoefficientMatieresEtablissements
        fields = '__all__'
        widgets = {
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class CoefficientMatiereParPeriodeForm(forms.ModelForm):
    class Meta:
        model = CoefficientMatiereParPeriode
        fields = '__all__'
        widgets = {
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'periode': forms.Select(attrs={'class': 'form-select'}),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control'}),
        }
