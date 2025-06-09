from django.db import models

from etablissements.models import Etablissements

# Create your models here.
class Actualites(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    date_publication = models.DateField(auto_now_add=True)
    cible = models.CharField(max_length=20, choices=[("tous", "Tous"), ("parents", "Parents"), ("personnel", "Personnel")])
    etablissement = models.ForeignKey(Etablissements, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="actualites/", null=True, blank=True)
    fichier = models.FileField(upload_to="actualites_fichiers/", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titre} - {self.etablissement.nom}"

    class Meta:
        ordering = ['-date_publication']
