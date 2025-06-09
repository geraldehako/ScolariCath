from django.db import models
import random
import string
from django.utils.timezone import now
from datetime import date
from authentifications.models import Utilisateurs
from cores.models import AnneeScolaires
from etablissements.models import Classes, Etablissements
from scolarites.models import Echeances, ModalitePaiements




# Create your models here.
class Parents(models.Model):
    utilisateur = models.OneToOneField(Utilisateurs, on_delete=models.CASCADE,null=True)
    nom_complet = models.CharField(max_length=150)
    telephone = models.CharField(max_length=10,unique=True,null=True,blank=True)
    email = models.EmailField(unique=True,null=True,blank=True)

class Eleves(models.Model):
    matricule = models.CharField(max_length=9, unique=True, blank=True, null=True)
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')])
    nationalite = models.CharField(max_length=100, null=True)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100, null=True, blank=True)
    photo = models.ImageField(upload_to='eleves/', null=True, blank=True)
    parent = models.ForeignKey('Parents', on_delete=models.SET_NULL, null=True, blank=True)
    origine = models.ForeignKey(Etablissements, on_delete=models.SET_NULL, null=True, blank=True)
    maladie_particuliere = models.CharField(max_length=250, null=True)
    religion = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenoms}"

    class Meta:
        verbose_name = "Élève"
        verbose_name_plural = "Élèves"

    def save(self, *args, **kwargs):
            # Normalisation
            if self.matricule == '':
                self.matricule = None

            # Génération du matricule si absent
            if not self.matricule:
                annee = now().year
                prefixe = "X"
                base = f"{prefixe}{annee}"
                count = Eleves.objects.filter(matricule__startswith=base).count() + 1
                numero = f"{count:04d}"
                matricule_genere = f"{base}{numero}"

                while Eleves.objects.filter(matricule=matricule_genere).exists():
                    count += 1
                    numero = f"{count:04d}"
                    matricule_genere = f"{base}{numero}"

                self.matricule = matricule_genere

            # Sauvegarde finale
            super().save(*args, **kwargs)


    def inscription_active(self):
        if not self.pk:
            return None
        return self.inscriptions_set.order_by('-annee_scolaire__date_debut').first()

    def paiements_par_annee(self):
        return {
            insc.annee_scolaire.nom: {
                "du": insc.montant_total_du(),
                "paye": insc.montant_total_paye(),
                "solde": insc.solde_restant(),
                "regle": insc.est_en_regle()
            }
            for insc in self.inscriptions_set.all()
        }
        
    def age(self):
        if self.date_naissance:
            today = date.today()
            return today.year - self.date_naissance.year - (
                (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
            )
        return None  # ou 0 ou autre valeur par défaut

        
class LienParente(models.Model):
    parent = models.ForeignKey(Parents, on_delete=models.CASCADE)
    eleve = models.ForeignKey(Eleves, on_delete=models.CASCADE)
    lien = models.CharField(max_length=20)  # père, mère, tuteur

from django.db.models import Sum    
class Inscriptions(models.Model):
    STATUT_CHOIX = [('affecte', 'Affecté'), ('non_affecte', 'Non Affecté')]
    ETAT_CHOIX = [('Present', 'Présent'), ('abandon', 'Abandon')]
    
    eleve = models.ForeignKey(Eleves, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classes, on_delete=models.CASCADE, null=True, blank=True)
    annee_scolaire = models.ForeignKey(AnneeScolaires, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=STATUT_CHOIX)
    date_inscription = models.DateField(auto_now_add=True)
    utilisateur = models.ForeignKey(Utilisateurs, on_delete=models.CASCADE)  # Utilisateur qui enregistre l'inscription
    etat = models.CharField(max_length=20, choices=ETAT_CHOIX, default='Present')
    reduction = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        help_text="Réduction accordée (en montant, pas en %)"
    )
    transport = models.BooleanField(default=False)
    cantine = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.eleve.nom} {self.eleve.prenoms} ({self.annee_scolaire.libelle})"

    class Meta:
        unique_together = ('eleve', 'annee_scolaire')
        
    def montant_total_du(self):
        from scolarites.models import Echeances  # import ici
        from django.db.models import Sum
        if self.statut == 'non_affecte':
            echeances = Echeances.objects.filter(
                modalite__annee_scolaire=self.annee_scolaire,
                modalite__niveau=self.classe.niveau,
                modalite__etablissement=self.classe.etablissement,
                modalite__applicable_aux_non_affectes=True
            )
        elif self.statut == 'affecte':
            echeances = Echeances.objects.filter(
                modalite__annee_scolaire=self.annee_scolaire,
                modalite__niveau=self.classe.niveau,
                modalite__etablissement=self.classe.etablissement,
            )
        else:
            return 0
        return echeances.aggregate(total=Sum('montant'))['total'] or 0


    def montant_total_paye(self):
        from scolarites.models import Paiements  # import ici
        from django.db.models import Sum
        return Paiements.objects.filter(
            inscription=self,
            statut_validation__in=['valide', 'partiel']
        ).aggregate(total=Sum('montant'))['total'] or 0

    def solde_restant(self):
        return self.montant_total_du() - self.montant_total_paye()

    def est_en_regle(self):
        return self.solde_restant() <= 0

    def echeances_non_soldees(self):
        from scolarites.models import Paiements, Echeances  # import ici

        # Récupérer toutes les échéances totalement payées
        echeances_payees = []
        if self.classe or self.statut == 'non_affecte':
            if self.statut == 'non_affecte':
                echeances = Echeances.objects.filter(
                    modalite__annee_scolaire=self.annee_scolaire,
                    modalite__niveau=self.classe.niveau,
                    modalite__etablissement=self.classe.etablissement,
                    modalite__applicable_aux_non_affectes=True
                )
            else:
                echeances = Echeances.objects.filter(
                   modalite__annee_scolaire=self.annee_scolaire,
                    modalite__niveau=self.classe.niveau,
                    modalite__etablissement=self.classe.etablissement,
                )

            for echeance in echeances:
                total_paye = Paiements.objects.filter(
                    inscription=self,
                    echeance=echeance,
                    statut_validation='valide'
                ).aggregate(total=Sum('montant'))['total'] or 0
                if total_paye >= echeance.montant:
                    echeances_payees.append(echeance.id)

            return echeances.exclude(id__in=echeances_payees)

        return Echeances.objects.none()


    def pourcentage_paye(self):
        total_du = self.montant_total_du()
        if total_du == 0:
            return 0
        return round((self.montant_total_paye() / total_du) * 100, 2)

    def statut_paiement_affichage(self):
        if self.est_en_regle():
            return "✅ En règle"
        elif self.montant_total_paye() > 0:
            return "🟡 Partiellement payé"
        else:
            return "🔴 Non payé"



class Scolarites(models.Model):
    inscription = models.OneToOneField(
        Inscriptions,
        on_delete=models.CASCADE,
        related_name='scolarite',
        help_text="Lien unique avec l'inscription"
    )
    modalite = models.ForeignKey(
        ModalitePaiements,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Modalité de paiement applicable"
    )
    date_attribution = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Scolarité - {self.inscription.eleve} ({self.inscription.annee_scolaire})"

class Relances(models.Model):
    STATUT_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    inscription = models.ForeignKey(Inscriptions, on_delete=models.CASCADE)
    echeance = models.ForeignKey(Echeances, on_delete=models.CASCADE)
    date_relance = models.DateField()
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='active')
    echeance_montant = models.PositiveIntegerField(blank=True, null=True)
    total_verse = models.PositiveIntegerField(blank=True, null=True)
    total_solde = models.PositiveIntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Calcul automatique du statut selon le solde
        if self.total_solde == 0:
            self.statut = 'inactive'
        else:
            self.statut = 'active'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.inscription.eleve.nom} - {self.echeance.nom} ({self.statut})"


class Mutations(models.Model):
    eleve = models.ForeignKey(Eleves, on_delete=models.CASCADE)
    ancienne_classe = models.ForeignKey(Classes, on_delete=models.SET_NULL, null=True, related_name='ancienne_classe')
    nouvelle_classe = models.ForeignKey(Classes, on_delete=models.SET_NULL, null=True, related_name='nouvelle_classe')
    date_mutation = models.DateField()
    motif = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Mutation de {self.eleve.nom} {self.eleve.prenoms}"

    def etablissements_associes(self):
        etablissements = []
        # On vérifie les classes associées (ancienne et nouvelle) et on récupère l'établissement
        if self.ancienne_classe:
            etablissements.append(self.ancienne_classe.etablissement)
        if self.nouvelle_classe:
            etablissements.append(self.nouvelle_classe.etablissement)
        return etablissements

    # Optionnel: Si tu veux obtenir un seul établissement, tu peux ajouter une méthode comme celle-ci:
    def etablissement_actuel(self):
        if self.nouvelle_classe:
            return self.nouvelle_classe.etablissement
        return None


class EvenementScolaire(models.Model):
    TYPE_EVENEMENT = [
        ('absence', 'Absence'),
        ('retard', 'Retard'),
        ('sanction', 'Sanction'),
        ('avertissement', 'Avertissement'),
        ('exclusion', 'Exclusion temporaire'),
        ('felicitation', 'Félicitations'),
        ('tableau_honneur', 'Tableau d\'honneur'),
        ('activite', 'Activité parascolaire'),
        ('reunion', 'Réunion parents-professeurs'),
        ('conseil', 'Conseil de classe'),
        ('autre', 'Autre'),
    ]

    eleve = models.ForeignKey(Eleves, on_delete=models.CASCADE, related_name="evenements")
    annee_scolaire = models.ForeignKey(AnneeScolaires, on_delete=models.CASCADE)
    type_evenement = models.CharField(max_length=30, choices=TYPE_EVENEMENT)
    titre = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date_evenement = models.DateField()
    responsable = models.CharField(max_length=100, help_text="Nom de la personne responsable (professeur, éducateur, etc.)")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_evenement']

    def __str__(self):
        return f"{self.type_evenement.title()} - {self.titre} ({self.eleve})"



#072c84 bleu
#ecde26 jaune
#eaecec blanc
#424f53 gris
#acb057 vert
