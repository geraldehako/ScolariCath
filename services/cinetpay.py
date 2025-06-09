# services/cinetpay.py
from cinetpay_sdk.s_d_k import Cinetpay
from django.conf import settings

client = Cinetpay(settings.CINETPAY_API_KEY, settings.CINETPAY_SITE_ID)

def init_cinetpay_payment(inscription, montant, transaction_id, return_url, notify_url):
    data = {
        'amount': montant,
        'currency': "XOF",
        'transaction_id': transaction_id,
        'description': f"Paiement pour {inscription.eleve.nom} {inscription.eleve.prenoms}",
        'return_url': return_url,
        'notify_url': notify_url,
        'customer_name': inscription.eleve.nom,
        'customer_surname': inscription.eleve.prenoms,
    }
    return client.PaymentInitialization(data)

from cinetpay_sdk.s_d_k import Cinetpay
import uuid

def init_cinetpay_payment2(inscription, montant_total, return_url, notify_url):
    client = Cinetpay(apikey="21585943f75164bbc2.38014639", site_id="296911")

    transaction_id = str(uuid.uuid4())  # Génère un ID unique

    data = {
        'amount': int(montant_total),
        'currency': "XOF",
        'transaction_id': transaction_id,
        'description': f"Paiement pour {inscription.eleve.nom_complet()}",
        'return_url': return_url,
        'notify_url': notify_url,
        'customer_name': inscription.eleve.nom,
        'customer_surname': inscription.eleve.prenoms,
    }

    result = client.PaymentInitialization(data)
    return result, transaction_id
