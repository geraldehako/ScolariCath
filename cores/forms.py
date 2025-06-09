from django import forms
from .models import Cycles, AnneeScolaires, Trimestres, Periodes

class CycleForm(forms.ModelForm):
    class Meta:
        model = Cycles
        fields = ['code', 'nom']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: P pour Primaire'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du cycle'
            }),
        }

class AnneeScolaireForm(forms.ModelForm):
    class Meta:
        model = AnneeScolaires
        fields = ['libelle', 'date_debut', 'date_fin', 'active']
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TrimestreForm(forms.ModelForm):
    class Meta:
        model = Trimestres
        fields = ['cycle', 'nom', 'date_debut', 'date_fin']
        widgets = {
            'cycle': forms.Select(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class PeriodeForm(forms.ModelForm):
    class Meta:
        model = Periodes
        fields = ['nom', 'ordre', 'annee_scolaire']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'ordre': forms.NumberInput(attrs={'class': 'form-control'}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-control'})
        }
