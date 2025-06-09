from datetime import timedelta
import os
from django.db import models
from django.utils import timezone
from django.conf import settings
from authentifications.models import Utilisateurs
from cores.models import AnneeScolaires
from etablissements.models import Etablissements, Niveaux
from django.db.models import Sum  # ✅ Correct

# Create your models here.
class ModalitePaiements(models.Model):
    nom = models.CharField(max_length=100)
    niveau = models.ForeignKey(Niveaux, on_delete=models.CASCADE, null=True)
    nombre_echeances = models.PositiveIntegerField()
    montant = models.PositiveIntegerField(help_text="Montant total à payer pour cette modalité", null=True)
    etablissement = models.ForeignKey(Etablissements, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaires, on_delete=models.CASCADE)
    applicable_aux_non_affectes = models.BooleanField(default=False)
 
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['etablissement', 'annee_scolaire', 'niveau','applicable_aux_non_affectes'],
                name='unique_modalite_par_etablissement_annee_niveau_applicable_aux_non_affectes'
            )
        ]

    def __str__(self):
        return f"{self.etablissement} - {self.niveau} - {self.nom} - {self.montant}"

    def generer_echeances(self):
        montant_par_echeance = self.montant // self.nombre_echeances
        reste = self.montant % self.nombre_echeances
        date_debut = timezone.now().date()
        for i in range(self.nombre_echeances):
            montant = montant_par_echeance + (1 if i == 0 and reste > 0 else 0)
            Echeances.objects.create(
                modalite=self,
                nom=f"Echéance {i + 1}",
                montant=montant,
                date_limite=date_debut + timedelta(days=30 * i)  # espacement mensuel
            )
            
            
    # models.py
    #def generer_echeances(self):
    #    if self.montant is None or self.nombre_echeances is None:
    #        raise ValueError("Le montant et le nombre d'échéances doivent être définis.")

    #    montant_par_echeance = self.montant // self.nombre_echeances
    #    reste = self.montant % self.nombre_echeances
    #    date_debut = timezone.now().date()
    #    for i in range(1, self.nombre_echeances + 1):
    #        montant = montant_par_echeance + (1 if i == 1 and reste > 0 else 0)
    #        Echeances.objects.create(
    #            modalite=self,
    #            nom=f"Echéance {i}",
    #            montant=montant,
    #            date_limite=date_debut + timedelta(days=30 * i)  # espacement mensuel  # à modifier manuellement après
    #        )

class Mois(models.Model):
    mois = models.CharField(max_length=100)

    def __str__(self):
        return self.mois

class ModaliteTransports(models.Model):
    nom = models.CharField(max_length=100)
    mois = models.ForeignKey(Mois, on_delete=models.CASCADE, null=True)
    #nombre_echeances = models.PositiveIntegerField()
    montant = models.PositiveIntegerField(help_text="Montant total à payer pour cette modalité", null=True)
    etablissement = models.ForeignKey(Etablissements, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaires, on_delete=models.CASCADE)
    #applicable_aux_non_affectes = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['etablissement', 'annee_scolaire', 'mois'],
                name='unique_modalite_transport_par_etablissement_annee_mois'
            )
        ]

    def __str__(self):
        return f"{self.etablissement} - {self.mois} - {self.nom} - {self.montant}"

class ModaliteCantines(models.Model):
    nom = models.CharField(max_length=100)
    mois = models.ForeignKey(Mois, on_delete=models.CASCADE, null=True)
    #nombre_echeances = models.PositiveIntegerField()
    montant = models.PositiveIntegerField(help_text="Montant total à payer pour cette modalité", null=True)
    etablissement = models.ForeignKey(Etablissements, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaires, on_delete=models.CASCADE)
    #applicable_aux_non_affectes = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['etablissement', 'annee_scolaire', 'mois'],
                name='unique_modalite_cantine_par_etablissement_annee_mois'
            )
        ]

    def __str__(self):
        return f"{self.etablissement} - {self.mois} - {self.nom} - {self.montant}"

class Echeances(models.Model):
    modalite = models.ForeignKey(ModalitePaiements, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    montant = models.PositiveIntegerField()
    date_limite = models.DateField()

    def __str__(self):
        return f"{self.nom} - {self.modalite.nom}"


def paiement_justificatif_path(instance, filename):
    # Justificatif sera stocké sous : justificatifs/2025/05/03/eleve_id_123_reçu.pdf
    return os.path.join("justificatifs", timezone.now().strftime("%Y/%m/%d"), f"eleve_id_{instance.inscription.eleve.id}_{filename}")

from django.core.exceptions import ValidationError
class Paiements(models.Model):
    MODES = [
        ('especes', 'Espèces'),
        ('virement', 'B.Free'),
        #('mobile_money', 'Mobile Money'),
        #('virement', 'Virement bancaire'),
        #('cheque', 'Chèque'),
        #('autre', 'Autre'),
    ]

    STATUTS_VALIDATION = [
        ('en_attente', 'En attente de validation'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
        ('partiel', 'Partiel'),
    ]

    inscription = models.ForeignKey('eleves.Inscriptions', on_delete=models.CASCADE)
    echeance = models.ForeignKey('Echeances', on_delete=models.CASCADE)
    montant = models.PositiveIntegerField()
    date_paiement = models.DateField()
    mode_paiement = models.CharField(max_length=20, choices=MODES)
    numero_transaction = models.CharField(max_length=100, blank=True, null=True)
    justificatif = models.FileField(upload_to=paiement_justificatif_path, blank=True, null=True)
    observations = models.TextField(blank=True, null=True)

    statut_validation = models.CharField(max_length=20, choices=STATUTS_VALIDATION, default='en_attente')
    date_validation = models.DateTimeField(null=True, blank=True)
    valide_par = models.ForeignKey(
        Utilisateurs,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='paiements_valides'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['numero_transaction'], name='unique_numero_transaction', condition=~models.Q(numero_transaction=None))
        ]
    
    def clean(self):
        # Vérifie l’unicité manuellement si la base ne la gère pas bien
        if self.numero_transaction:
            if Paiements.objects.exclude(pk=self.pk).filter(numero_transaction=self.numero_transaction).exists():
                raise ValidationError({'numero_transaction': "Ce numéro de transaction existe déjà."})

    def save(self, *args, **kwargs):
        if self.mode_paiement == 'especes' and not self.numero_transaction:
            now = timezone.now()
            self.numero_transaction = f"ES{now.strftime('%Y%m%d%H%M%S')}"
        self.full_clean()  # Appelle clean() avant sauvegarde
        super().save(*args, **kwargs)
    
    def valider(self, user):
        PaiementHistoriques.objects.create(
        paiement=self,
        utilisateur=user,
        action="validation",
        ancien_statut=self.statut_validation,
        nouveau_statut="valide",
        ancien_montant=self.montant,
        nouveau_montant=self.montant,
        commentaire="Paiement validé."
        )
        self.statut_validation = 'valide'
        self.date_validation = timezone.now()
        self.valide_par = user
        self.save()

    def rejeter(self, user):
        PaiementHistoriques.objects.create(
            paiement=self,
            utilisateur=user,
            action="rejet",
            ancien_statut=self.statut_validation,
            nouveau_statut="rejete",
            ancien_montant=self.montant,
            nouveau_montant=self.montant,
            commentaire="Paiement rejeté."
        )
        self.statut_validation = 'rejete'
        self.date_validation = timezone.now()
        self.valide_par = user
        self.save()


    def __str__(self):
        return f"{self.inscription.eleve.nom} - {self.montant} ({self.get_mode_paiement_display()})"

    class Meta:
        ordering = ['-date_paiement']

class PaiementsTransports(models.Model):
    MODES = [
        ('especes', 'Espèces'),
        ('virement', 'B.Free'),
        #('mobile_money', 'Mobile Money'),
        #('virement', 'Virement bancaire'),
        #('cheque', 'Chèque'),
        #('autre', 'Autre'),
    ]

    STATUTS_VALIDATION = [
        ('en_attente', 'En attente de validation'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
        ('partiel', 'Partiel'),
    ]

    inscription = models.ForeignKey('eleves.Inscriptions', on_delete=models.CASCADE)
    echeance = models.ForeignKey(ModaliteTransports, on_delete=models.CASCADE)
    montant = models.PositiveIntegerField()
    date_paiement = models.DateField()
    mode_paiement = models.CharField(max_length=20, choices=MODES)
    numero_transaction = models.CharField(max_length=100, blank=True, null=True)
    justificatif = models.FileField(upload_to=paiement_justificatif_path, blank=True, null=True)
    observations = models.TextField(blank=True, null=True)

    statut_validation = models.CharField(max_length=20, choices=STATUTS_VALIDATION, default='en_attente')
    date_validation = models.DateTimeField(null=True, blank=True)
    valide_par = models.ForeignKey(
        Utilisateurs,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='paiements_transports_valides'
    )
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['numero_transaction'], name='unique_numero_transaction', condition=~models.Q(numero_transaction=None))
        ]
    
    def clean(self):
        # Vérifie l’unicité manuellement si la base ne la gère pas bien
        if self.numero_transaction:
            if Paiements.objects.exclude(pk=self.pk).filter(numero_transaction=self.numero_transaction).exists():
                raise ValidationError({'numero_transaction': "Ce numéro de transaction existe déjà."})

    def save(self, *args, **kwargs):
        if self.mode_paiement == 'especes' and not self.numero_transaction:
            now = timezone.now()
            self.numero_transaction = f"ES{now.strftime('%Y%m%d%H%M%S')}"
        self.full_clean()  # Appelle clean() avant sauvegarde
        super().save(*args, **kwargs)

    def valider(self, user):
        PaiementTransportHistoriques.objects.create(
        paiement=self,
        utilisateur=user,
        action="validation",
        ancien_statut=self.statut_validation,
        nouveau_statut="valide",
        ancien_montant=self.montant,
        nouveau_montant=self.montant,
        commentaire="Paiement validé."
        )
        self.statut_validation = 'valide'
        self.date_validation = timezone.now()
        self.valide_par = user
        self.save()

    def rejeter(self, user):
        PaiementTransportHistoriques.objects.create(
            paiement=self,
            utilisateur=user,
            action="rejet",
            ancien_statut=self.statut_validation,
            nouveau_statut="rejete",
            ancien_montant=self.montant,
            nouveau_montant=self.montant,
            commentaire="Paiement rejeté."
        )
        self.statut_validation = 'rejete'
        self.date_validation = timezone.now()
        self.valide_par = user
        self.save()


    def __str__(self):
        return f"{self.inscription.eleve.nom} - {self.montant} ({self.get_mode_paiement_display()})"

    class Meta:
        ordering = ['-date_paiement']


class PaiementsCantines(models.Model):
    MODES = [
        ('especes', 'Espèces'),
        ('virement', 'B.Free'),
        #('mobile_money', 'Mobile Money'),
        #('virement', 'Virement bancaire'),
        #('cheque', 'Chèque'),
        #('autre', 'Autre'),
    ]

    STATUTS_VALIDATION = [
        ('en_attente', 'En attente de validation'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
        ('partiel', 'Partiel'),
    ]

    inscription = models.ForeignKey('eleves.Inscriptions', on_delete=models.CASCADE)
    echeance = models.ForeignKey(ModaliteCantines, on_delete=models.CASCADE)
    montant = models.PositiveIntegerField()
    date_paiement = models.DateField()
    mode_paiement = models.CharField(max_length=20, choices=MODES)
    numero_transaction = models.CharField(max_length=100, blank=True, null=True)
    justificatif = models.FileField(upload_to=paiement_justificatif_path, blank=True, null=True)
    observations = models.TextField(blank=True, null=True)

    statut_validation = models.CharField(max_length=20, choices=STATUTS_VALIDATION, default='en_attente')
    date_validation = models.DateTimeField(null=True, blank=True)
    valide_par = models.ForeignKey(
        Utilisateurs,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='paiements_cantines_valides'
    )
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['numero_transaction'], name='unique_numero_transaction', condition=~models.Q(numero_transaction=None))
        ]
    
    def clean(self):
        # Vérifie l’unicité manuellement si la base ne la gère pas bien
        if self.numero_transaction:
            if Paiements.objects.exclude(pk=self.pk).filter(numero_transaction=self.numero_transaction).exists():
                raise ValidationError({'numero_transaction': "Ce numéro de transaction existe déjà."})

    def save(self, *args, **kwargs):
        if self.mode_paiement == 'especes' and not self.numero_transaction:
            now = timezone.now()
            self.numero_transaction = f"ES{now.strftime('%Y%m%d%H%M%S')}"
        self.full_clean()  # Appelle clean() avant sauvegarde
        super().save(*args, **kwargs)

    def valider(self, user):
        PaiementCantinesHistoriques.objects.create(
        paiement=self,
        utilisateur=user,
        action="validation",
        ancien_statut=self.statut_validation,
        nouveau_statut="valide",
        ancien_montant=self.montant,
        nouveau_montant=self.montant,
        commentaire="Paiement validé."
        )
        self.statut_validation = 'valide'
        self.date_validation = timezone.now()
        self.valide_par = user
        self.save()

    def rejeter(self, user):
        PaiementCantinesHistoriques.objects.create(
            paiement=self,
            utilisateur=user,
            action="rejet",
            ancien_statut=self.statut_validation,
            nouveau_statut="rejete",
            ancien_montant=self.montant,
            nouveau_montant=self.montant,
            commentaire="Paiement rejeté."
        )
        self.statut_validation = 'rejete'
        self.date_validation = timezone.now()
        self.valide_par = user
        self.save()


    def __str__(self):
        return f"{self.inscription.eleve.nom} - {self.montant} ({self.get_mode_paiement_display()})"

    class Meta:
        ordering = ['-date_paiement']


class PaiementMobileEnAttente(models.Model):
    inscription = models.ForeignKey('eleves.Inscriptions', on_delete=models.CASCADE)
    echeance = models.ForeignKey('Echeances', on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    statut_validation = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente'),
        ('valide', 'Valide'),
        ('annule', 'Annulé'),
    ], default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)

    def valider(self):
        """Valide le paiement et crée l'enregistrement dans la table principale Paiements"""
        from .models import Paiements  # import local pour éviter circular import
        Paiements.objects.create(
            inscription=self.inscription,
            echeance=self.relance.echeance,
            montant=self.montant,
            date_paiement=timezone.now().date(),
            mode_paiement='mobile_money',
            statut_validation='valide',
            valide_par=None
        )

        # Mettre à jour la relance
        self.relance.total_verse = (self.relance.total_verse or 0) + self.montant
        self.relance.total_solde = max(self.relance.echeance_montant - self.relance.total_verse, 0)
        self.relance.save()

        self.statut_validation = 'valide'
        self.date_validation = timezone.now()
        self.save()




class PaiementHistoriques(models.Model):
    paiement = models.ForeignKey("Paiements", on_delete=models.CASCADE, related_name="historiques")
    utilisateur = models.ForeignKey(Utilisateurs, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)  # Ex: "création", "modification", "validation", "rejet"
    ancien_statut = models.CharField(max_length=20, blank=True, null=True)
    nouveau_statut = models.CharField(max_length=20, blank=True, null=True)
    ancien_montant = models.PositiveIntegerField(blank=True, null=True)
    nouveau_montant = models.PositiveIntegerField(blank=True, null=True)
    date_action = models.DateTimeField(auto_now_add=True)
    commentaire = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date_action.strftime('%d/%m/%Y %H:%M')} - {self.utilisateur} - {self.action}"

class PaiementTransportHistoriques(models.Model):
    paiement = models.ForeignKey("PaiementsTransports", on_delete=models.CASCADE, related_name="historiques")
    utilisateur = models.ForeignKey(Utilisateurs, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)  # Ex: "création", "modification", "validation", "rejet"
    ancien_statut = models.CharField(max_length=20, blank=True, null=True)
    nouveau_statut = models.CharField(max_length=20, blank=True, null=True)
    ancien_montant = models.PositiveIntegerField(blank=True, null=True)
    nouveau_montant = models.PositiveIntegerField(blank=True, null=True)
    date_action = models.DateTimeField(auto_now_add=True)
    commentaire = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date_action.strftime('%d/%m/%Y %H:%M')} - {self.utilisateur} - {self.action}"
    
class PaiementCantinesHistoriques(models.Model):
    paiement = models.ForeignKey("PaiementsCantines", on_delete=models.CASCADE, related_name="historiques")
    utilisateur = models.ForeignKey(Utilisateurs, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)  # Ex: "création", "modification", "validation", "rejet"
    ancien_statut = models.CharField(max_length=20, blank=True, null=True)
    nouveau_statut = models.CharField(max_length=20, blank=True, null=True)
    ancien_montant = models.PositiveIntegerField(blank=True, null=True)
    nouveau_montant = models.PositiveIntegerField(blank=True, null=True)
    date_action = models.DateTimeField(auto_now_add=True)
    commentaire = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date_action.strftime('%d/%m/%Y %H:%M')} - {self.utilisateur} - {self.action}"