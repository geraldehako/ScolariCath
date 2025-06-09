from django.db import models
from authentifications.models import Utilisateurs
from cores.models import AnneeScolaires
from etablissements.models import Etablissements
from django.core.exceptions import ValidationError

class Caisses(models.Model):
    nom = models.CharField(max_length=100)
    etablissement = models.ForeignKey(Etablissements, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaires, on_delete=models.CASCADE)
    solde_initial = models.PositiveIntegerField(default=0)
    date_creation = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('etablissement', 'annee_scolaire', 'nom')
        verbose_name = "Caisse"
        verbose_name_plural = "Caisses"

    def __str__(self):
        return f"{self.nom} ({self.etablissement.nom})"

    def solde_courant(self):
        total_depenses = self.depenses.filter(statut_validation="valide").aggregate(total=models.Sum('montant'))['total'] or 0
        return self.solde_initial - total_depenses
    
    def depenses_en_attente(self):
        total_depenses_en_attente = self.depenses.filter(statut_validation="en_attente").aggregate(total=models.Sum('montant'))['total'] or 0
        return total_depenses_en_attente


class Depenses(models.Model):
    MOTIFS = [
        ("tables", "Réparation de tables-bancs"),
        ("iep", "Transport IEP"),
        ("direction", "Transport école - Direction"),
        ("admin", "Courses administratives"),
        ("fournitures", "Achat fournitures"),
        ("travaux", "Travaux divers"),
        ("entretien", "Entretien des locaux"),
    ]

    STATUTS_VALIDATION = [
        ('en_attente', 'En attente de validation'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
        ('partiel', 'Partiellement validé'),
    ]

    caisse = models.ForeignKey(Caisses, on_delete=models.CASCADE, related_name='depenses')
    motif = models.CharField(max_length=100, choices=MOTIFS)
    montant = models.PositiveIntegerField()
    date_depense = models.DateField()
    responsable = models.ForeignKey(Utilisateurs, on_delete=models.SET_NULL, null=True, blank=True)
    justificatif = models.FileField(upload_to='justificatifs/', null=True, blank=True)
    statut_validation = models.CharField(max_length=20, choices=STATUTS_VALIDATION, default='en_attente')
    date_validation = models.DateTimeField(null=True, blank=True)
    commentaire = models.TextField(blank=True)
    annee_scolaire = models.ForeignKey(AnneeScolaires, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-date_depense']
        verbose_name = "Dépense"
        verbose_name_plural = "Dépenses"

    def __str__(self):
        return f"{self.date_depense} - {self.get_motif_display()} - {self.montant} FCFA"



class CaisseCentrales(models.Model):
    nom = models.CharField(max_length=100, default="Caisse Centrale")
    solde_initial = models.PositiveIntegerField(default=0)
    date_creation = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nom

    @property
    def solde_courant(self):
        total_entrees = self.operations.filter(type_operation='entree').aggregate(
            total=models.Sum('montant'))['total'] or 0
        total_sorties = self.operations.filter(type_operation='sortie').aggregate(
            total=models.Sum('montant'))['total'] or 0
        return total_entrees - total_sorties

    def solde_entrees(self):
        total_entrees = self.operations.filter(type_operation='entree').aggregate(
            total=models.Sum('montant'))['total'] or 0
        return total_entrees  # ✅ Corrigé

    def solde_sorties(self):
        total_sorties = self.operations.filter(type_operation='sortie').aggregate(
            total=models.Sum('montant'))['total'] or 0
        return total_sorties  # ✅ Corrigé
    


class Operations(models.Model):
    TYPES_OPERATION = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
    ]

    MOTIFS_SORTIE = [
        ("tables", "Réparation de tables-bancs"),
        ("iep", "Transport IEP"),
        ("direction", "Transport école - Direction"),
        ("admin", "Courses administratives"),
        ("fournitures", "Achat fournitures"),
        ("travaux", "Travaux divers"),
        ("entretien", "Entretien des locaux"),
    ]

    caisse = models.ForeignKey(CaisseCentrales, on_delete=models.CASCADE, related_name='operations')
    type_operation = models.CharField(max_length=6, choices=TYPES_OPERATION)
    motif = models.CharField(max_length=100, blank=True, null=True)
    montant = models.PositiveIntegerField()
    date_operation = models.DateField()
    responsable = models.ForeignKey(Utilisateurs, on_delete=models.SET_NULL, null=True, blank=True)
    justificatif = models.FileField(upload_to='justificatifs/', null=True, blank=True)
    commentaire = models.TextField(blank=True)
    annee_scolaire = models.ForeignKey(AnneeScolaires, on_delete=models.CASCADE)
    etablissement = models.ForeignKey(Etablissements, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.date_operation} - {self.get_type_operation_display()} - {self.montant} FCFA"

    def clean(self):
        # Validation motif obligatoire pour sortie
        if self.type_operation == 'sortie' and not self.motif:
            raise ValidationError('Le motif est obligatoire pour une sortie.')

        # Validation présence caisse et fonds disponibles pour sortie
        if self.type_operation == 'sortie':
            if not self.caisse:
                raise ValidationError("La caisse est obligatoire pour valider une sortie.")

            # Calcul du solde disponible dans la caisse (hors opération en cours)
            total_entree = self.caisse.operations.filter(type_operation='entree').aggregate(total=models.Sum('montant'))['total'] or 0
            total_sortie = self.caisse.operations.filter(type_operation='sortie').exclude(id=self.id).aggregate(total=models.Sum('montant'))['total'] or 0
            solde_disponible = total_entree - total_sortie

            if self.montant > solde_disponible:
                raise ValidationError(f"Fonds insuffisants : le solde disponible est de {solde_disponible} FCFA.")
