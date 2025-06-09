from django.db import models
from django.core.exceptions import ValidationError  # Corrigé ici
from cores.models import AnneeScolaires, Cycles


class TypeEtablissement(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nom

class Etablissements(models.Model):
    nom = models.CharField(max_length=255)
    types = models.ManyToManyField(Cycles, related_name='etablissements')
    adresse = models.TextField()
    localisation = models.CharField(max_length=255)
    code_etablissement = models.CharField(max_length=50, unique=True)
    directeur = models.ForeignKey(
        "authentifications.Utilisateurs",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,  # 👈 autorise les valeurs vides dans le formulaire
        related_name="dirige"
    )
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    def __str__(self):
        types_str = ", ".join([t.nom for t in self.types.all()])
        return f"{self.nom} ({types_str})"
    
    @property
    def nb_eleves_inscrits(self):
        from inscriptions.models import Inscriptions  # adapte selon ton app
        return Inscriptions.objects.filter(
            inscription_classe__etablissement=self
        ).count()




class Niveaux(models.Model):
    nom = models.CharField(max_length=50)
    cycle = models.ForeignKey(Cycles, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nom} - {self.cycle.nom}"


class Classes(models.Model):
    nom = models.CharField(max_length=50)
    niveau = models.ForeignKey(Niveaux, on_delete=models.CASCADE)
    etablissement = models.ForeignKey(Etablissements, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaires, on_delete=models.CASCADE)
    capacite = models.PositiveIntegerField()

    class Meta:
        unique_together = ("nom", "etablissement", "annee_scolaire")

    def est_complete(self):
        return self.inscription_set.count() >= self.capacite

    def nb_eleves(self):
        return self.inscriptions_set.count() if hasattr(self, 'inscriptions_set') else 0

    def est_pleine(self):
        return self.nb_eleves() >= self.capacite

    def __str__(self):
        return f"{self.nom} - {self.niveau.nom} ({self.etablissement.nom})"


class EmploiTemps(models.Model):
    from matieres.models import Matieres  # 👈 déplacer ici pour éviter l'import circulaire
    from enseignants.models import Enseignants,TenueDeClasse  # 👈 déplacer ici pour éviter l'import circulaire
    JOURS_SEMAINE = [
        ('lundi', 'Lundi'),
        ('mardi', 'Mardi'),
        ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'),
        ('vendredi', 'Vendredi'),
        ('samedi', 'Samedi'),
    ]

    jour = models.CharField(max_length=10, choices=JOURS_SEMAINE)
    classe = models.ForeignKey(Classes, on_delete=models.CASCADE)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    matiere = models.ForeignKey(Matieres, on_delete=models.CASCADE)
    professeur = models.ForeignKey(Enseignants, on_delete=models.CASCADE,null=True, blank=True)
    tennant = models.ForeignKey(TenueDeClasse, on_delete=models.CASCADE,null=True, blank=True)
    class Meta:
        unique_together = ("classe", "jour", "heure_debut")

    def __str__(self):
        return f"{self.classe.nom} - {self.jour} ({self.heure_debut} à {self.heure_fin})"

    def chevauchement(self):
        return EmploiTemps.objects.filter(
            classe=self.classe,
            jour=self.jour,
            heure_debut__lt=self.heure_fin,
            heure_fin__gt=self.heure_debut
        ).exclude(id=self.id).exists()
