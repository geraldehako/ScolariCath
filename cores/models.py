from django.db import models
from datetime import timedelta
# Create your models here.

class Cycles(models.Model):
    code = models.CharField(max_length=2, unique=True, null=True)  # Ex : P, C, M
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom

class AnneeScolaires(models.Model):
    libelle = models.CharField(max_length=11, unique=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle

    def generer_periodes_selon_cycle(self):
        # Supprimer toutes les périodes de cette année
        Periodes.objects.filter(annee_scolaire=self).delete()

        cycles = Cycles.objects.all()
        ordre = 1  # Pour garder l'ordre des périodes

        for cycle in cycles:
            duree_totale = (self.date_fin - self.date_debut).days + 1

            if cycle.nom.lower() in ['préscolaire', 'primaire']:
                nb_periodes = 4
                prefixe = "Composition"
            elif cycle.nom.lower() in ['collège', 'lycée']:
                nb_periodes = 3
                prefixe = "Trimestre"
            elif cycle.nom.lower() == 'technique':
                nb_periodes = 2
                prefixe = "Semestre"
            else:
                continue  # ignorer les cycles non reconnus

            duree_par_periode = duree_totale // nb_periodes
            date_debut = self.date_debut

            for i in range(nb_periodes):
                date_fin = date_debut + timedelta(days=duree_par_periode - 1)
                # Ne pas dépasser la date de fin de l’année
                if date_fin > self.date_fin or i == nb_periodes - 1:
                    date_fin = self.date_fin

                Periodes.objects.create(
                    nom=f"{prefixe} {i + 1}",
                    ordre=ordre,
                    annee_scolaire=self,
                    cycle=cycle  # 🔴 Ajout du cycle ici
                )
                ordre += 1
                date_debut = date_fin + timedelta(days=1)



    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.generer_periodes_selon_cycle()


class Trimestres(models.Model):
    cycle = models.ForeignKey(Cycles, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    date_debut = models.DateField()
    date_fin = models.DateField()

    def __str__(self):
        return f"{self.nom} ({self.cycle.nom})"

class Periodes(models.Model):
    nom = models.CharField(max_length=50)
    ordre = models.PositiveIntegerField()
    annee_scolaire = models.ForeignKey(AnneeScolaires, on_delete=models.CASCADE)
    cycle = models.ForeignKey(Cycles, on_delete=models.CASCADE,null=True)

    class Meta:
        unique_together = ('ordre', 'annee_scolaire')
        ordering = ['ordre']

    def __str__(self):
        return f"{self.nom} - {self.annee_scolaire.libelle} - {self.cycle.nom}"


