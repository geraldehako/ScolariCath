from django.db import models
from authentifications.models import Utilisateurs
from cores.models import AnneeScolaires
from etablissements.models import Classes, Etablissements
from matieres.models import Matieres

# Create your models here.
class Postes(models.Model):
    nom = models.CharField(max_length=100)
    role_attache = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.nom


class Personnels(models.Model):
    utilisateur = models.OneToOneField(Utilisateurs, on_delete=models.CASCADE)
    nom_complet = models.CharField(max_length=150)
    poste = models.ForeignKey(Postes, on_delete=models.SET_NULL, null=True, blank=True)
    photo = models.ImageField(upload_to='personnel/', null=True, blank=True)
    etablissement = models.ForeignKey(Etablissements, on_delete=models.CASCADE,null=True, blank=True)
    date_embauche = models.DateField()

    STATUT_CHOICES = [
        ("actif", "Actif"),
        ("muté", "Muté"),
        ("sorti", "Sorti"),
    ]
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="actif")
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Personnel"
        verbose_name_plural = "Personnels"

    def __str__(self):
        poste_nom = self.poste.nom if self.poste else "Sans poste"
        return f"{self.nom_complet} - {poste_nom} ({self.etablissement.nom})"

    @property
    def statut_affichage(self):
        return dict(self.STATUT_CHOICES).get(self.statut, "Inconnu")

    def mutations(self):
        return self.mutationpersonnel_set.all()

    @property
    def telephone(self):
        return self.utilisateur.telephone

    @property
    def email(self):
        return self.utilisateur.email


class MutationPersonnel(models.Model):
    personnel = models.ForeignKey(Personnels, on_delete=models.CASCADE)
    etablissement_source = models.ForeignKey(Etablissements, on_delete=models.CASCADE, related_name='mutations_envoyees')
    etablissement_destination = models.ForeignKey(Etablissements, on_delete=models.CASCADE, related_name='mutations_recues')
    date_mutation = models.DateField()
    motif = models.TextField()

    def __str__(self):
        return f"Mutation de {self.personnel.nom_complet} de {self.etablissement_source.nom} à {self.etablissement_destination.nom}"

class Enseignants(Personnels):
    specialite = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nom_complet} - {self.specialite}"

class TenueDeClasse(models.Model):
    enseignant = models.ForeignKey(Personnels, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classes, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaires, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.enseignant.nom_complet} - {self.classe.nom} ({self.annee_scolaire.libelle})"

class Affectation(models.Model):
    professseur = models.ForeignKey(Enseignants, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classes, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matieres, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaires, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.enseignant.nom_complet} - {self.matiere.nom} - {self.classe.nom} ({self.annee_scolaire.libelle})"
