from django import forms
from .models import Roles, Utilisateurs, AccesFonctionnalites
from django.contrib.auth.forms import UserCreationForm

class RoleForm(forms.ModelForm):
    class Meta:
        model = Roles
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UtilisateurForm(forms.ModelForm):
    class Meta:
        model = Utilisateurs
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'photo', 'role', 'etablissement', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(),
        }
        
class UtilisateurSecreForm(forms.ModelForm): 
    class Meta:
        model = Utilisateurs
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'photo', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        # Filtrer le champ poste comme role
        self.fields['role'].queryset = Roles.objects.filter(nom__in=['Secrétaire Exécutif', 'Trésorerie', 'Comptabilité'])
        
class UtilisateurEconForm(forms.ModelForm): 
    class Meta:
        model = Utilisateurs
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'photo', 'role', 'etablissement', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        # Filtrer le champ poste comme role
        self.fields['role'].queryset = Roles.objects.filter(nom__in=['Économat'])
        
class UtilisateurPersForm(forms.ModelForm): 
    class Meta:
        model = Utilisateurs
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'photo', 'role', 'etablissement', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        # Filtrer le champ poste comme role
        self.fields['role'].queryset = Roles.objects.filter(nom__in=['Professeurs','Enseignants'])
        
class UtilisateurPareForm(forms.ModelForm): 
    class Meta:
        model = Utilisateurs
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'photo', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        # Filtrer le champ poste comme role
        self.fields['role'].queryset = Roles.objects.filter(nom__in=['Parents'])
        
class UtilisateurDirecForm(forms.ModelForm): 
    class Meta:
        model = Utilisateurs
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'photo', 'role', 'etablissement', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        # Filtrer le champ poste comme role
        self.fields['role'].queryset = Roles.objects.filter(nom__in=['Direction'])
 

from django.contrib.auth.forms import UserChangeForm
class UtilisateurUpdateForm(UserChangeForm):
    password = None  # Ne pas afficher le champ password par défaut

    nouveau_mot_de_passe = forms.CharField(
        label='Nouveau mot de passe',
        widget=forms.PasswordInput,
        required=True
    )
    confirmation_mot_de_passe = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput,
        required=True
    )

    class Meta:
        model = Utilisateurs
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        mot_de_passe = cleaned_data.get('nouveau_mot_de_passe')
        confirmation = cleaned_data.get('confirmation_mot_de_passe')

        if mot_de_passe and mot_de_passe != confirmation:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        utilisateur = super().save(commit=False)
        mot_de_passe = self.cleaned_data.get('nouveau_mot_de_passe')
        if mot_de_passe:
            utilisateur.set_password(mot_de_passe)
            utilisateur.pwd = mot_de_passe  # facultatif
        if commit:
            utilisateur.save()
        return utilisateur
    
class AccesFonctionnaliteForm(forms.ModelForm):
    class Meta:
        model = AccesFonctionnalites
        fields = ['role', 'fonctionnalite', 'code', 'autorise']
        widgets = {
            'fonctionnalite': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'autorise': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
