from django.db import models

from cores.models import AnneeScolaires, Periodes
from eleves.models import Eleves
from enseignants.models import Enseignants
from matieres.models import Matieres
from notes.appreciations import generer_appreciation, generer_mention
from notes.utils import calculer_moyenne_par_periode

# Create your models here.
class TypeEvaluation(models.Model):
    libelle = models.CharField(max_length=100)
    bareme = models.PositiveIntegerField(default=20)

    def __str__(self):
        return f"{self.libelle} (/{self.bareme})"


class Notes(models.Model):
    eleve = models.ForeignKey(Eleves, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matieres, on_delete=models.CASCADE)
    periode = models.ForeignKey(Periodes, on_delete=models.CASCADE)
    enseignant = models.ForeignKey(Enseignants, on_delete=models.SET_NULL, null=True)
    valeur = models.DecimalField(max_digits=5, decimal_places=2)
    type_evaluation = models.ForeignKey(TypeEvaluation, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.eleve.nom} - {self.matiere.nom} : {self.valeur}/{self.type_evaluation.bareme if self.type_evaluation else '?'}"


class Bulletins(models.Model):
    eleve = models.ForeignKey(Eleves, on_delete=models.CASCADE)
    periode = models.ForeignKey(Periodes, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaires, on_delete=models.CASCADE)
    moyenne_generale = models.DecimalField(max_digits=5, decimal_places=2)
    rang = models.PositiveIntegerField()
    appreciation = models.TextField()
    mention = models.CharField(max_length=20, blank=True)
    decision_conseil = models.TextField(blank=True)
    fichier_pdf = models.FileField(upload_to='bulletins/')
 

    def generer_bulletin(eleve, periode, annee_scolaire, etablissement):
        moyenne = calculer_moyenne_par_periode(eleve, periode, etablissement)
    
        bulletin, created = Bulletins.objects.update_or_create(
            eleve=eleve,
            periode=periode,
            annee_scolaire=annee_scolaire,
            defaults={
                'moyenne_generale': moyenne,
                'appreciation': generer_appreciation(moyenne),
                'mention': generer_mention(moyenne),
                # ajouter les autres champs si nécessaire
            }
        )
        return bulletin
