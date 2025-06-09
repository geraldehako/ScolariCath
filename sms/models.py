from django.db import models

# Create your models here.
class NotificationSMS(models.Model):
    TYPE_CHOIX = [
        ('relance_paiement', 'Relance paiement'),
        ('info_generale', 'Information générale'),
        ('alerte', 'Alerte'),
    ]

    types = models.CharField(max_length=50, choices=TYPE_CHOIX, blank=True, null=True)
    destinataire = models.CharField(max_length=100)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    envoye = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.destinataire} - {self.date_envoi.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        ordering = ['-date_envoi']

class TentativeEnvoi(models.Model):
    notification = models.ForeignKey(NotificationSMS, on_delete=models.CASCADE, related_name='tentatives')
    date_tentative = models.DateTimeField(auto_now_add=True)
    succes = models.BooleanField(default=False)
    message_erreur = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Tentative {self.date_tentative.strftime('%d/%m/%Y %H:%M')} - Success: {self.succes}"