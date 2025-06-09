# forms.py
from django import forms
from .models import Caisses, Depenses, Operations

class CaisseForm(forms.ModelForm):
    class Meta:
        model = Caisses
        fields = ['nom', 'etablissement', 'annee_scolaire', 'solde_initial']

class DepenseForm(forms.ModelForm):
    class Meta:
        model = Depenses
        fields = ['motif', 'montant', 'date_depense', 'justificatif','commentaire']
        widgets = {
            # 'caisse': forms.Select(attrs={'class': 'form-control'}),
            'motif': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'date_depense': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'justificatif': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            # 'statut_validation': forms.Select(attrs={'class': 'form-control'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }



class OperationForm(forms.ModelForm):
    class Meta:
        model = Operations
        fields = ['type_operation', 'motif', 'montant', 'date_operation', 'justificatif', 'commentaire']
        widgets = {
            'type_operation': forms.Select(attrs={'class': 'form-select'}),
            'motif': forms.Select(attrs={'class': 'form-select'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_operation': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'justificatif': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['motif'].required = False
        self.fields['motif'].widget.choices = [('', '---------')] + Operations.MOTIFS_SORTIE
