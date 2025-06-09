from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.timezone import now

# Create your models here.
class Roles(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        nouveau = self.pk is None
        super().save(*args, **kwargs)
        if nouveau:
            from authentifications.permissions import assigner_fonctionnalites_par_defaut
            assigner_fonctionnalites_par_defaut(self) 
    
    def est_utilise(self):
        return self.utilisateurs_set.exists()

class Utilisateurs(AbstractUser):
    from etablissements.models import Etablissements  # 👈 déplacer ici pour éviter l'import circulaire
    photo = models.ImageField(
        upload_to='utilisateurs/photos/',
        null=True,
        blank=True,
        help_text="Photo de profil de l'utilisateur"
    )
    role = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True)
    etablissement = models.ForeignKey(Etablissements, on_delete=models.SET_NULL, null=True, blank=True)
    telephone = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        help_text="Numéro de téléphone de l'utilisateur" 
    )
    pwd = models.CharField(
        max_length=12,
        null=True,
        blank=True,
        help_text="pwd de l'utilisateur" 
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['telephone'],
                condition=~models.Q(telephone=None),
                name='unique_telephone_not_null'
            )
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.role.nom if self.role else 'Sans rôle'}"

    @property
    def nom_complet(self):
        return f"{self.first_name} {self.last_name}".strip()

    def clean(self):
        super().clean()
        if self.telephone:
            if not self.telephone.isdigit():
                raise ValidationError("Le numéro de téléphone doit contenir uniquement des chiffres.")
            if len(self.telephone) != 10:
                raise ValidationError("Le numéro de téléphone doit contenir exactement 10 chiffres.")
    
class AccesFonctionnalites(models.Model):
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)
    fonctionnalite = models.CharField(max_length=100)
    code = models.SlugField(max_length=100)  # ex: 'consulter_les_notes'
    autorise = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.role.nom} - {self.fonctionnalite} : {'Oui' if self.autorise else 'Non'}"
    
class HistoriqueConnexion(models.Model):
    utilisateur = models.ForeignKey(Utilisateurs, on_delete=models.CASCADE)
    type_evenement = models.CharField(max_length=20, choices=[('connexion', 'Connexion'), ('deconnexion', 'Déconnexion')])
    date_heure = models.DateTimeField(default=now)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.utilisateur.username} - {self.type_evenement} - {self.date_heure.strftime('%d/%m/%Y %H:%M:%S')}"