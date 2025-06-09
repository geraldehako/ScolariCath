from django import forms

from authentifications.models import Roles, Utilisateurs
from cores.models import AnneeScolaires
from etablissements.models import Classes
from .models import Postes, Personnels, MutationPersonnel, TenueDeClasse, Affectation

class PosteForm(forms.ModelForm):
    class Meta:
        model = Postes
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du poste'
            }),
        }


class PersonnelForm(forms.ModelForm):
    # Champs liés au modèle Utilisateurs
    telephone = forms.CharField(
        max_length=10, 
        required=True, 
        help_text="Numéro de téléphone de l'utilisateur"
    )
    email = forms.EmailField(
        required=True,
        help_text="Adresse email de l'utilisateur"
    )
    role = forms.ModelChoiceField(
        queryset=Roles.objects.all(),
        required=True,
        help_text="Sélectionner le rôle de l'utilisateur"
    )

    class Meta:
        model = Personnels
        fields = [
            'nom_complet', 'poste', 'photo', 'etablissement', 
            'date_embauche', 'statut', 'actif'
        ]
        widgets = {
            'nom_complet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet'}),
            'poste': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}), 
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des champs utilisateur
        self.fields['telephone'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-select'})
        
        
class PersonnelSecreForm(forms.ModelForm):
    # Champs liés au modèle Utilisateurs 
    telephone = forms.CharField(
        max_length=10, 
        required=True, 
        help_text="Numéro de téléphone de l'utilisateur"
    )
    email = forms.EmailField(
        required=True,
        help_text="Adresse email de l'utilisateur"
    )
    role = forms.ModelChoiceField(
        queryset=Roles.objects.filter(nom__in=['Secrétaire Exécutif', 'Trésorerie', 'Comptabilité']),
        required=True,
        help_text="Sélectionner le rôle de l'utilisateur"
    )


    class Meta:
        model = Personnels
        fields = [
            'nom_complet', 'poste', 'photo', 'etablissement', 
            'date_embauche', 'statut', 'actif'
        ]
        widgets = {
            'nom_complet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet'}),
            'poste': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}), 
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des champs utilisateur
        self.fields['telephone'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-select'})
        
        # Filtrer le champ poste comme role
        self.fields['poste'].queryset = Postes.objects.filter(role_attache__in=['Secrétaire Exécutif', 'Trésorerie', 'Comptabilité'])

class PersonnelDirecForm(forms.ModelForm):
    # Champs liés au modèle Utilisateurs 
    telephone = forms.CharField(
        max_length=10, 
        required=True, 
        help_text="Numéro de téléphone de l'utilisateur"
    )
    email = forms.EmailField(
        required=True,
        help_text="Adresse email de l'utilisateur"
    )
    role = forms.ModelChoiceField(
        queryset=Roles.objects.filter(nom__in=['Direction']),
        required=True,
        help_text="Sélectionner le rôle de l'utilisateur"
    )


    class Meta:
        model = Personnels
        fields = [
            'nom_complet', 'poste', 'photo', 'etablissement', 
            'date_embauche', 'statut', 'actif'
        ]
        widgets = {
            'nom_complet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet'}),
            'poste': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}), 
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des champs utilisateur
        self.fields['telephone'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-select'})
        
        # Filtrer le champ poste comme role
        self.fields['poste'].queryset = Postes.objects.filter(role_attache__in=['Direction'])

class PersonnelEconForm(forms.ModelForm):
    # Champs liés au modèle Utilisateurs
    telephone = forms.CharField(
        max_length=10, 
        required=True, 
        help_text="Numéro de téléphone de l'utilisateur"
    )
    email = forms.EmailField(
        required=True,
        help_text="Adresse email de l'utilisateur"
    )
    role = forms.ModelChoiceField(
        queryset=Roles.objects.filter(nom__in=['Économat']),
        required=True,
        help_text="Sélectionner le rôle de l'utilisateur"
    )


    class Meta:
        model = Personnels
        fields = [
            'nom_complet', 'poste', 'photo', 'etablissement', 
            'date_embauche', 'statut', 'actif'
        ]
        widgets = {
            'nom_complet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet'}),
            'poste': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}), 
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des champs utilisateur
        self.fields['telephone'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-select'})
        
        # Filtrer le champ poste comme role
        self.fields['poste'].queryset = Postes.objects.filter(role_attache__in=['Économat', 'Trésorerie', 'Comptabilité'])
        
class PersonnelProfForm(forms.ModelForm):
    # Champs liés au modèle Utilisateurs
    telephone = forms.CharField(
        max_length=10, 
        required=True, 
        help_text="Numéro de téléphone de l'utilisateur"
    )
    email = forms.EmailField(
        required=True,
        help_text="Adresse email de l'utilisateur"
    )
    role = forms.ModelChoiceField(
        queryset=Roles.objects.filter(nom__in=['Professeurs']),
        required=True,
        help_text="Sélectionner le rôle de l'utilisateur"
    )


    class Meta:
        model = Personnels
        fields = [
            'nom_complet', 'poste', 'photo', 'etablissement', 
            'date_embauche', 'statut', 'actif'
        ]
        widgets = {
            'nom_complet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet'}),
            'poste': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}), 
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des champs utilisateur
        self.fields['telephone'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-select'})
        
        # Filtrer le champ poste comme role
        self.fields['poste'].queryset = Postes.objects.filter(role_attache__in=['Professeur'])
        
class PersonnelAdjoiForm(forms.ModelForm):
    # Champs liés au modèle Utilisateurs
    telephone = forms.CharField(
        max_length=10, 
        required=True, 
        help_text="Numéro de téléphone de l'utilisateur"
    )
    email = forms.EmailField(
        required=True,
        help_text="Adresse email de l'utilisateur"
    )
    role = forms.ModelChoiceField(
        queryset=Roles.objects.filter(nom__in=['Enseignants']),
        required=True,
        help_text="Sélectionner le rôle de l'utilisateur"
    )


    class Meta:
        model = Personnels
        fields = [
            'nom_complet', 'poste', 'photo', 'etablissement', 
            'date_embauche', 'statut', 'actif'
        ]
        widgets = {
            'nom_complet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet'}),
            'poste': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}), 
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des champs utilisateur
        self.fields['telephone'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-select'})
        
        # Filtrer le champ poste comme role
        self.fields['poste'].queryset = Postes.objects.filter(role_attache__in=['Adjoint'])

class PersonnelEtForm(forms.ModelForm):
    # Champs liés au modèle Utilisateurs
    telephone = forms.CharField(
        max_length=10, 
        required=True, 
        help_text="Numéro de téléphone de l'utilisateur"
    )
    email = forms.EmailField(
        required=True,
        help_text="Adresse email de l'utilisateur"
    )

    class Meta:
        model = Personnels
        fields = [
            'nom_complet', 'photo', 
            'date_embauche', 'statut', 'actif'
        ]
        widgets = {
            'nom_complet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}), 
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des champs utilisateur
        self.fields['telephone'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})


class TenueDeClasseForm(forms.ModelForm):
    class Meta:
        model = TenueDeClasse
        fields = ['classe']
        widgets = {
            'classe': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            etablissement = user.etablissement
            annee_active = AnneeScolaires.objects.filter(active=True).first()
            if etablissement and annee_active:
                self.fields['classe'].queryset = Classes.objects.filter(
                    etablissement=etablissement,
                    annee_scolaire=annee_active
                )

        
class PersonnelFormZ(forms.ModelForm):
    telephone = forms.CharField(
        max_length=10, 
        required=True, 
        help_text="Numéro de téléphone de l'utilisateur"
    )
    email = forms.EmailField(
        required=True,
        help_text="Adresse email de l'utilisateur"
    )
    role = forms.ModelChoiceField(
        queryset=Roles.objects.all(),
        required=True,
        help_text="Sélectionner le rôle de l'utilisateur"
    )

    class Meta:
        model = Personnels
        fields = [
            'nom_complet', 'poste', 'photo', 'etablissement', 
            'date_embauche', 'statut', 'actif', 'telephone', 'email', 'role'
        ]
        widgets = {
            'nom_complet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l’établissement'}),
            'poste': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}), 
            'etablissement': forms.Select(attrs={'class': 'form-select'}),
            'date_embauche': forms.TextInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }




class PersonnelFormm(forms.ModelForm):
    telephone = forms.CharField(
        max_length=10,
        required=True,
        help_text="Numéro de téléphone de l'utilisateur"
    )
    email = forms.EmailField(
        required=True,
        help_text="Adresse email de l'utilisateur"
    )

    class Meta:
        model = Personnels
        fields = [
            'nom_complet', 'poste', 'photo', 'etablissement',
            'date_embauche', 'statut', 'actif'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.utilisateur:
            self.fields['telephone'].initial = self.instance.utilisateur.telephone
            self.fields['email'].initial = self.instance.utilisateur.email

    def save(self, commit=True):
        personnel = super().save(commit=False)

        # Créer ou mettre à jour l'utilisateur associé
        if not personnel.utilisateur_id:
            utilisateur = Utilisateurs.objects.create(
                username=self.cleaned_data['telephone'],
                telephone=self.cleaned_data['telephone'],
                email=self.cleaned_data['email'],
                first_name=personnel.nom_complet.split(' ')[0],
                last_name=' '.join(personnel.nom_complet.split(' ')[1:]),
                etablissement=personnel.etablissement,
            )
            utilisateur.set_password('12345678')  # vous pouvez générer un mot de passe aléatoire ici
            utilisateur.save()
            personnel.utilisateur = utilisateur
        else:
            utilisateur = personnel.utilisateur
            utilisateur.telephone = self.cleaned_data['telephone']
            utilisateur.email = self.cleaned_data['email']
            utilisateur.save()

        if commit:
            personnel.save()

        return personnel

class EnseignantForm(PersonnelForm):
    specialite = forms.CharField(required=False)

    class Meta(PersonnelForm.Meta):
        fields = PersonnelForm.Meta.fields + ['specialite']


class MutationPersonnelForm(forms.ModelForm):
    class Meta:
        model = MutationPersonnel
        fields = '__all__'

class TenueDeClasseFormONE(forms.ModelForm):
    class Meta:
        model = TenueDeClasse
        fields = '__all__'

class AffectationForm(forms.ModelForm):
    class Meta:
        model = Affectation
        fields = '__all__'

