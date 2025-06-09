from rest_framework import serializers

from authentifications.models import Roles, Utilisateurs
from eleves.models import Eleves, Inscriptions, Parents, Relances
from etablissements.models import Classes
from scolarites.models import ModaliteCantines, ModaliteTransports, Paiements, PaiementsCantines, PaiementsTransports
from django.db.models import Sum

class ModaliteCantinesSerializer(serializers.ModelSerializer):
    mois = serializers.CharField(source='mois.mois')  # renvoie "Janvier", pas l'ID
    class Meta:
        model = ModaliteCantines
        fields = ['id', 'nom', 'mois', 'montant']

class ModaliteTransportsSerializer(serializers.ModelSerializer):
    mois = serializers.CharField(source='mois.mois')  # renvoie "Janvier", pas l'ID
    class Meta:
        model = ModaliteTransports
        fields = ['id', 'nom', 'mois', 'montant']
        


class EleveInscritSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='eleve.id')
    nom = serializers.CharField(source='eleve.nom')
    prenom = serializers.CharField(source='eleve.prenoms')
    matricule = serializers.CharField(source='eleve.matricule')
    classe = serializers.CharField(source='classe.nom')
    
    scolarite = serializers.SerializerMethodField()
    paye = serializers.SerializerMethodField()
    solde = serializers.SerializerMethodField()

    class Meta:
        model = Inscriptions
        fields = ['matricule', 'nom', 'prenom', 'classe', 'scolarite', 'paye', 'solde','id']

    def get_scolarite(self, obj):
        return obj.montant_total_du()

    def get_paye(self, obj):
        return obj.montant_total_paye()

    def get_solde(self, obj):
        return obj.solde_restant()



class EleveDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eleves
        fields = ['id','matricule', 'nom', 'prenoms', 'date_naissance', 'lieu_naissance', 'sexe']


class ClasseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classes
        fields = ['id', 'nom']


from django.utils import timezone
class PaiementSerializer(serializers.ModelSerializer):
    relance = serializers.IntegerField(write_only=True)

    class Meta:
        model = Paiements
        fields = '__all__'  # relance est maintenant inclus car déclaré au-dessus

    def validate(self, data):
        montant = data.get('montant')
        mode = data.get('mode_paiement')

        if montant <= 0:
            raise serializers.ValidationError("Le montant doit être supérieur à zéro.")
        
        if mode not in ['especes', 'mobile_money']:
            raise serializers.ValidationError("Mode de paiement invalide.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        inscription = validated_data['inscription']
        echeance = validated_data['echeance']
        montant = validated_data['montant']
        mode = validated_data['mode_paiement']
        relance_id = validated_data.pop('relance')  # Important: on retire le champ non-model ici

        # Définir le statut selon le mode de paiement
        if mode == 'especes':
            statut = 'valide'
            valide_par = request.user if request else None
        else:
            statut = 'en_attente'
            valide_par = None

        # Création du paiement
        paiement = Paiements.objects.create(
            inscription=inscription,
            echeance=echeance,
            montant=montant,
            date_paiement=timezone.now().date(),
            mode_paiement=mode,
            statut_validation=statut,
            valide_par=valide_par,
        )

        # Mise à jour de la relance associée
        try:
            relance = Relances.objects.get(id=relance_id, inscription=inscription)
            relance.total_verse = (relance.total_verse or 0) + montant
            relance.total_solde = max((relance.echeance_montant or 0) - relance.total_verse, 0)
            relance.save()
        except Relances.DoesNotExist:
            pass  # Optionnel : logguer ou ignorer si la relance n'existe pas

        return paiement


class PaiementTransportSerializer(serializers.ModelSerializer):
    #relance = serializers.IntegerField(write_only=True)

    class Meta:
        model = PaiementsTransports
        fields = '__all__'  # relance est maintenant inclus car déclaré au-dessus

    def validate(self, data):
        montant = data.get('montant')
        mode = data.get('mode_paiement')

        if montant <= 0:
            raise serializers.ValidationError("Le montant doit être supérieur à zéro.")
        
        if mode not in ['especes', 'mobile_money']:
            raise serializers.ValidationError("Mode de paiement invalide.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        inscription = validated_data['inscription']
        echeance = validated_data['echeance']
        #echeance = validated_data.pop('relance')  # Important: on retire le champ non-model ici
        montant = validated_data['montant']
        mode = validated_data['mode_paiement']
        #relance_id = validated_data.pop('relance')  # Important: on retire le champ non-model ici

        # Définir le statut selon le mode de paiement
        if mode == 'especes':
            statut = 'valide'
            valide_par = request.user if request else None
        else:
            statut = 'en_attente'
            valide_par = None

        # Création du paiement
        paiement = PaiementsTransports.objects.create(
            inscription=inscription,
            echeance=echeance,
            montant=montant,
            date_paiement=timezone.now().date(),
            mode_paiement=mode,
            statut_validation=statut,
            valide_par=valide_par,
        )

    # Mise à jour de la relance associée
        #try:
        #    relance = Relances.objects.get(id=relance_id, inscription=inscription)
        #    relance.total_verse = (relance.total_verse or 0) + montant
        #    relance.total_solde = max((relance.echeance_montant or 0) - relance.total_verse, 0)
        #    relance.save()
        #except Relances.DoesNotExist:
        #    pass  # Optionnel : logguer ou ignorer si la relance n'existe pas

        return paiement


class PaiementCantineSerializer(serializers.ModelSerializer):
    #relance = serializers.IntegerField(write_only=True)

    class Meta:
        model = PaiementsCantines
        fields = '__all__'  # relance est maintenant inclus car déclaré au-dessus

    def validate(self, data):
        montant = data.get('montant')
        mode = data.get('mode_paiement')

        if montant <= 0:
            raise serializers.ValidationError("Le montant doit être supérieur à zéro.")
        
        if mode not in ['especes', 'mobile_money']:
            raise serializers.ValidationError("Mode de paiement invalide.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        inscription = validated_data['inscription']
        echeance = validated_data['echeance']
        montant = validated_data['montant']
        mode = validated_data['mode_paiement']
        #relance_id = validated_data.pop('relance')  # Important: on retire le champ non-model ici

        # Définir le statut selon le mode de paiement
        if mode == 'especes':
            statut = 'valide'
            valide_par = request.user if request else None
        else:
            statut = 'en_attente'
            valide_par = None

        # Création du paiement
        paiement = PaiementsCantines.objects.create(
            inscription=inscription,
            echeance=echeance,
            montant=montant,
            date_paiement=timezone.now().date(),
            mode_paiement=mode,
            statut_validation=statut,
            valide_par=valide_par,
        )

        # Mise à jour de la relance associée
        #try:
        #    relance = Relances.objects.get(id=relance_id, inscription=inscription)
        #    relance.total_verse = (relance.total_verse or 0) + montant
        #    relance.total_solde = max((relance.echeance_montant or 0) - relance.total_verse, 0)
        #    relance.save()
        #except Relances.DoesNotExist:
        #    pass  # Optionnel : logguer ou ignorer si la relance n'existe pas

        return paiement
    
    
from rest_framework import serializers
    
class EleveSerializer(serializers.ModelSerializer):
    nom = serializers.CharField(source='nom.upper', read_only=True)
    prenom = serializers.CharField(source='prenom.title', read_only=True)
    classe = serializers.SerializerMethodField()
    scolarite = serializers.SerializerMethodField()
    paye = serializers.SerializerMethodField()
    solde = serializers.SerializerMethodField()
    inscription_active = serializers.SerializerMethodField()

    class Meta:
        model = Eleves
        fields = ['id', 'matricule', 'nom', 'prenom', 'classe', 'scolarite', 'paye', 'solde', 'inscription_active']

    def get_classe(self, obj):
        inscription = self.get_active_inscription(obj)
        return inscription.classe.nom if inscription and inscription.classe else ""

    def get_scolarite(self, obj):
        inscription = self.get_active_inscription(obj)
        return inscription.montant_total if inscription else 0

    def get_paye(self, obj):
        inscription = self.get_active_inscription(obj)
        return inscription.montant_paye if inscription else 0

    def get_solde(self, obj):
        inscription = self.get_active_inscription(obj)
        if inscription:
            return (inscription.montant_total or 0) - (inscription.montant_paye or 0)
        return 0

    def get_inscription_active(self, obj):
        return self.get_active_inscription(obj) is not None

    def get_active_inscription(self, obj):
        from scolari.models import AnneeScolaire
        annee_active = AnneeScolaire.objects.filter(active=True).first()
        if not annee_active:
            return None
        return Inscriptions.objects.filter(eleve=obj, annee_scolaire=annee_active).select_related('classe').first()

# serializers.py


class EleveWriteSerializerUnOK(serializers.ModelSerializer):
    parent = serializers.DictField(write_only=True)

    class Meta:
        model = Eleves
        fields = ['matricule', 'nom', 'prenoms', 'sexe', 'date_naissance',
                  'lieu_naissance', 'nationalite', 'maladie_particuliere', 'parent']

    def create(self, validated_data):
        parent_data = validated_data.pop('parent', {})
        parent, _ = Parents.objects.get_or_create(
            telephone=parent_data.get('telephone'),
            defaults={
                "nom_complet": parent_data.get("nom_complet"),
                "email": parent_data.get("email"),
            }
        )
        eleve = Eleves.objects.create(parent=parent, **validated_data)
        return eleve


from django.contrib.auth.hashers import make_password

class EleveWriteSerializer(serializers.ModelSerializer):
    parent = serializers.DictField(write_only=True)

    class Meta:
        model = Eleves
        fields = ['matricule', 'nom', 'prenoms', 'sexe', 'date_naissance',
                  'lieu_naissance', 'nationalite', 'maladie_particuliere', 'parent']

    def create(self, validated_data):
        parent_data = validated_data.pop('parent', {})

        telephone = parent_data.get('telephone')
        nom_complet = parent_data.get('nom_complet')
        email = parent_data.get('email', '')

        # Vérifie si le parent existe déjà
        parent, parent_created = Parents.objects.get_or_create(
            telephone=telephone,
            defaults={
                "nom_complet": nom_complet,
                "email": email
            }
        )

        # Création du compte utilisateur si nécessaire
        if not hasattr(parent, 'utilisateur') or not parent.utilisateur:
            role, _ = Roles.objects.get_or_create(nom="Parents")

            # Découpe le nom complet si possible
            noms = nom_complet.strip().split()
            nom = noms[0]
            prenom = ' '.join(noms[1:]) if len(noms) > 1 else ''

            user, created = Utilisateurs.objects.get_or_create(
                username=telephone,
                defaults={
                    'first_name': prenom,
                    'last_name': nom,
                    'email': email,
                    'password': make_password(telephone),
                    'telephone': telephone,
                    'role': role
                }
            )

            if created:
                user.save()

            # Associer l'utilisateur au parent
            parent.utilisateur = user
            parent.save()

        # Création de l’élève
        eleve = Eleves.objects.create(parent=parent, **validated_data)
        return eleve
