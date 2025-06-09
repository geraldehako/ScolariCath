from django.db import models

from cores.models import Cycles, Periodes
from etablissements.models import Etablissements, Niveaux

# Create your models here.
class Matieres(models.Model):
    nom = models.CharField(max_length=100)
    obligatoire = models.BooleanField(default=True)
    cycle = models.ForeignKey(Cycles, on_delete=models.CASCADE)
    niveau = models.ForeignKey(Niveaux, on_delete=models.CASCADE,null=True)

    #def __str__(self):
    #    return f"{self.nom} - {self.niveau.nom} - {self.cycle.nom}"
    def __str__(self):
        return self.nom if self.nom else "Matière sans nom"


class CoefficientMatieres(models.Model): # Mathématiques – 6e → coef 4     Mathématiques – 3e → coef 5
    matiere = models.ForeignKey(Matieres, on_delete=models.CASCADE)
    niveau = models.ForeignKey(Niveaux, on_delete=models.CASCADE)
    coefficient = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('matiere', 'niveau')

    def __str__(self):
        return f"{self.matiere.nom} / {self.niveau.nom} → Coef {self.coefficient}"

class CoefficientMatieresEtablissements(models.Model):
    matiere = models.ForeignKey(Matieres, on_delete=models.CASCADE)
    niveau = models.ForeignKey(Niveaux, on_delete=models.CASCADE)
    etablissement = models.ForeignKey(Etablissements, on_delete=models.CASCADE)
    coefficient = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('matiere', 'niveau', 'etablissement')

    def __str__(self):
        return f"{self.matiere.nom} / {self.niveau.nom} - {self.etablissement.nom} → Coef {self.coefficient}"



class CoefficientMatiereParPeriode(models.Model):
    matiere = models.ForeignKey(Matieres, on_delete=models.CASCADE)
    niveau = models.ForeignKey(Niveaux, on_delete=models.CASCADE)
    etablissement = models.ForeignKey(Etablissements, on_delete=models.CASCADE)
    periode = models.ForeignKey(Periodes, on_delete=models.CASCADE)
    coefficient = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('matiere', 'niveau', 'etablissement', 'periode')

    def __str__(self):
        return f"{self.matiere.nom} - {self.niveau.nom} - {self.periode.nom} ({self.etablissement.nom}) → Coef {self.coefficient}"
