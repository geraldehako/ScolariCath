from django import forms
from django.forms import modelformset_factory

from cores.models import AnneeScolaires, Periodes
from matieres.models import Matieres
from .models import Notes, TypeEvaluation

class TypeEvaluationForm(forms.ModelForm):
    class Meta:
        model = TypeEvaluation
        fields = ['libelle', 'bareme']
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex : Devoir'}),
            'bareme': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class SelectionMatierePeriodeFormBON(forms.Form):
    matiere = forms.ModelChoiceField(queryset=Matieres.objects.none(), label="Matière", widget=forms.Select(attrs={'class': 'form-control'}))
    periode = forms.ModelChoiceField(queryset=Periodes.objects.none(), label="Période", widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        niveau_id = kwargs.pop('niveau_id', None)
        super().__init__(*args, **kwargs)

        if niveau_id:
            self.fields['matiere'].queryset = Matieres.objects.filter(niveau_id=niveau_id)

        annee_active = AnneeScolaires.objects.filter(active=True).first()
        if annee_active:
            self.fields['periode'].queryset = Periodes.objects.filter(annee_scolaire=annee_active).order_by('ordre')

class SelectionMatierePeriodeForm(forms.Form):
    matiere = forms.ModelChoiceField(
        queryset=Matieres.objects.none(),
        label="Matière",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    periode = forms.ModelChoiceField(
        queryset=Periodes.objects.none(),
        label="Période",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        niveau_id = kwargs.pop('niveau_id', None)
        cycle_id = kwargs.pop('cycle_id', None)  # 🔹 Ajout de cycle_id
        super().__init__(*args, **kwargs)

        if niveau_id:
            self.fields['matiere'].queryset = Matieres.objects.filter(niveau_id=niveau_id)

        annee_active = AnneeScolaires.objects.filter(active=True).first()
        if annee_active and cycle_id:
            self.fields['periode'].queryset = Periodes.objects.filter(
                annee_scolaire=annee_active,
                cycle_id=cycle_id
            ).order_by('ordre')


class NoteForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ['valeur']
        widgets = {
            'valeur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        }

NoteFormSet = modelformset_factory(Notes, form=NoteForm, extra=0)
