"""Prologicielsucces URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

from authentifications.views import CustomAuthToken, EleveViewSet, EnfantsDuParentAPIView, EvenementsParentAPIView, ListeElevesDirectionAPIView, PaiementCantineViewSet, PaiementCreateView, PaiementTransportViewSet, PaiementViewSet, PaiementsParTypeAPIView, PaiementsParTypeDirectionAPIView, PaiementsParTypeSecretariatAPIView, ParentDashboardView, RelancesEleveAPIView, ajouter_eleve_api, ajouter_inscription_api, api_direction_elevesoptiondeux, api_eleves_secretariat, api_fiche_eleve, api_fiche_enfants, api_liste_classes, api_liste_classes_inscription, api_liste_enseignants, api_liste_enseignants_secretariat, api_liste_etablissements, basculer_activation_utilisateur, creer_acces, creer_role, ajouter_utilisateur, dashboard_administrateur, dashboard_direction, dashboard_direction_api, dashboard_parent, dashboard_secretariat, dashboard_tresorerie, eleve_par_matricule, espace_parent, gestion_acces_role, historique_connexions, liste_acces, liste_acces_economat, liste_acces_etablissement, liste_acces_parent, liste_acces_personnels, liste_acces_secretariat, liste_roles, liste_utilisateurs, liste_utilisateurs_economat, liste_utilisateurs_etablissement, liste_utilisateurs_parent, liste_utilisateurs_personnel, liste_utilisateurs_secretariat, login_view, logout_userbank, logout_view, maj_acces_ajax, modalites_cantine_non_payees, modalites_transport_non_payees, modifier_role, modifier_utilisateur, modifier_utilisateur_direc, modifier_utilisateur_econo, modifier_utilisateur_pare, modifier_utilisateur_pers, modifier_utilisateur_pwd, modifier_utilisateur_secre, no_access, no_access_back, supprimer_role, supprimer_utilisateur
from caisses.views import ajouter_caisse, ajouter_depense, ajouter_operation, detail_caisse, detail_caisse_principale, enregistrer_dotation, export_operations_excel, export_operations_pdf, liste_caisses, liste_caisses_etablissement, liste_depenses, liste_depenses_caisse, liste_operations, liste_operations_points, modifier_caisse, modifier_depense, modifier_depense_back, modifier_operation, supprimer_caisse, supprimer_depense, supprimer_operation
from cores.views import activer_annee_scolaire, ajouter_annee_scolaire, ajouter_cycle, ajouter_periode, ajouter_trimestre, generer_trimestres, liste_annees_scolaires, liste_cycles, liste_periodes, liste_trimestres, modifier_annee_scolaire, modifier_cycle, modifier_periode, modifier_trimestre, supprimer_annee_scolaire, supprimer_cycle, supprimer_periode, supprimer_trimestre
from eleves.views import ajouter_eleve, ajouter_eleve_back, ajouter_eleve_etablissement, ajouter_eleveprerempli, ajouter_inscription, ajouter_lien, bulletins_eleve, classes_avec_eleves_inscrits, detail_eleve, detail_eleve_parent, detail_paiement, effectif_par_niveau_genre, effectif_par_niveau_genre_abandon_etablissement, effectif_par_niveau_genre_abandon_tous_etablissements, effectif_par_niveau_genre_etablissement, effectif_par_niveau_genre_sec, eleves_inscrits_abandon_etablissement, eleves_inscrits_abandon_tous, eleves_inscrits_etablissement, eleves_inscrits_reduction_etablissement, eleves_inscrits_reduction_tous, envoyer_sms_relances, export_effectif_abandon_global_excel, export_effectif_abandon_global_pdf, export_effectif_excel, export_effectif_excel_etablissement, export_effectif_excel_etablissement_abandon, export_effectif_excel_sec, export_effectif_pdf, export_effectif_pdf_etablissement, export_effectif_pdf_etablissement_abandon, export_effectif_pdf_sec, export_eleves_inscrits_abandon_excel, export_eleves_inscrits_abandon_pdf, export_eleves_inscrits_abandon_tous_excel, export_eleves_inscrits_abandon_tous_pdf, export_eleves_inscrits_excel, export_eleves_inscrits_pdf, export_eleves_inscrits_reduction_excel, export_eleves_inscrits_reduction_pdf, export_eleves_inscrits_reduction_tous_excel, export_eleves_inscrits_reduction_tous_pdf, export_relances_classe_excel, export_relances_classe_pdf, export_relances_excel, export_relances_pdf, export_relances_secretariat_excel, export_relances_secretariat_pdf, fiche_eleve, import_eleves, import_eleves_back,  liste_eleves, liste_eleves_back, liste_eleves_etablissement, liste_eleves_etablissement_start, liste_eleves_inscrits_par_classe, liste_eleves_systeme, liste_enfants, liste_liens, liste_liens_back, liste_relances, liste_relances_classe_non_a_jour, liste_relances_non_a_jour, liste_relances_secretariat_non_a_jour, modifier_eleve, modifier_lien, muter_eleves, paiements_eleve, rapport_export_etatscolarite_classe_affecte_excel, rapport_export_etatscolarite_classe_affecte_pdf, rapport_export_etatscolarite_classe_excel, rapport_export_etatscolarite_classe_non_affecte_excel, rapport_export_etatscolarite_classe_non_affecte_pdf, rapport_export_etatscolarite_classe_pdf, rapport_export_etatscolarite_secretariat_affecte_excel, rapport_export_etatscolarite_secretariat_affecte_pdf, rapport_export_etatscolarite_secretariat_excel, rapport_export_etatscolarite_secretariat_nonaffecte_excel, rapport_export_etatscolarite_secretariat_nonaffecte_pdf, rapport_export_etatscolarite_secretariat_pdf, rapport_export_relances_excel, rapport_export_relances_pdf, supprimer_eleve, supprimer_lien, tableau_etatscolarite_affecte_par_secretariat, tableau_etatscolarite_nonaffecte_par_secretariat, tableau_etatscolarite_par_etablissement_secretariat, tableau_etatscolarite_pour_etablissement_classe, tableau_etatscolarite_pour_etablissement_classe_abandons, tableau_etatscolarite_pour_etablissement_classe_affecte, tableau_etatscolarite_pour_etablissement_classe_nonaffecte, tableau_etatscolarite_pour_etablissement_classe_presents, tableau_etatscolarite_pour_secretariat_classe_abandons, tableau_etatscolarite_pour_secretariat_classe_presents, tableau_relances_par_etablissement, traitement_matricule
from enseignants.views import ajouter_affectation, ajouter_mutation, ajouter_tenue_classe, ajouter_tenue_de_classe, creer_personnel, creer_personnel_adjoint, creer_personnel_direction, creer_personnel_economat, creer_personnel_etablissement, creer_personnel_professeur, creer_personnel_secretariat, creer_poste, export_enseignants_excel, export_enseignants_pdf, liste_affectations, liste_enseignants, liste_mutations, liste_personnels, liste_personnels_economat, liste_personnels_etablissement, liste_personnels_instituteurs, liste_personnels_professeurs, liste_personnels_secretariat, liste_postes, liste_tenue_classe, modifier_affectation, modifier_mutation, modifier_personnel, modifier_personnel_adjoint, modifier_personnel_economat, modifier_personnel_etablissement, modifier_personnel_professeur, modifier_personnel_secretariat, modifier_poste, modifier_tenue_classe, supprimer_affectation, supprimer_mutation, supprimer_personnel, supprimer_poste, supprimer_tenue_classe
from etablissements.views import calendrier_emploi_classe, classes_etablissement, creer_classe, creer_classe_etablissement, creer_emploi_temps, creer_emploi_temps_primaire, creer_etablissement, creer_niveau, creer_typeetablissement, detail_etablissement, emploi_temps_etablissement_pdf, emploi_temps_pdf, etablissements_par_cycle, get_professeurs_par_matiere, liste_classes, liste_emploi, liste_etablissements, liste_niveaux, liste_typeetablissement, modifier_classe, modifier_classe_etablissement, modifier_emploi, modifier_emploi_primaire, modifier_etablissement, modifier_niveau, modifier_typeetablissement, supprimer_classe, supprimer_emploi, supprimer_etablissement, supprimer_niveau, supprimer_typeetablissement
from matieres.views import ajouter_coefficient, ajouter_matiere, creer_coefficient, creer_coefficient_etablissement, creer_coefficient_periode, creer_matiere, liste_coefficients, liste_coefficients_etablissement, liste_coefficients_periode, liste_matieres, liste_matieres_etablissements, modifier_coefficient, modifier_matiere, supprimer_coefficient, supprimer_matiere
from notes.views import ajouter_notes_classe, creer_type_evaluation, liste_type_evaluations, modifier_notes_classe, modifier_type_evaluation, selectionner_matiere_periode, supprimer_type_evaluation, voir_notes_classe
from scolarites.views import afficher_niveaux_et_modalites, ajouter_echeance, ajouter_modalite_cantine, ajouter_modalite_transport, ajouter_paiement, ajouter_paiement_parent, bilan_paiements_par_nature, bilan_paiements_par_nature_back, bilan_paiements_par_nature_cantine, bilan_paiements_par_nature_cantine_back, bilan_paiements_par_nature_transport, bilan_paiements_par_nature_transport_back, cantine_non_payees, cinetpay_notify, creer_echeance, creer_modalite, creer_mois, detail_echeances_modalite_back, detail_modalite, export_paiements_arrieres_excel, export_paiements_arrieres_excel_back, export_paiements_arrieres_pdf, export_paiements_arrieres_pdf_back, export_paiements_cantine_excel, export_paiements_cantine_excel_back, export_paiements_cantine_pdf, export_paiements_cantine_pdf_back, export_paiements_excel, export_paiements_excel_back, export_paiements_pdf, export_paiements_pdf_back, export_paiements_transport_excel, export_paiements_transport_excel_back, export_paiements_transport_pdf, export_paiements_transport_pdf_back, init_cinetpay, init_cinetpay_view, liste_echeances, liste_echeances_groupes, liste_modalites, liste_modalites_etablissement_back, liste_mois, liste_paiements_arrieres_back, liste_paiements_arrieres_etablissement, liste_paiements_back, liste_paiements_back_cantine, liste_paiements_back_transport, liste_paiements_etablissement, liste_paiements_etablissement_cantine, liste_paiements_etablissement_transport, modalites_cantine, modalites_transport, modifier_echeance, modifier_echeances_modalite, modifier_modalite, modifier_modalite_cantine, modifier_modalite_transport, modifier_mois, recu_paiement_pdf, supprimer_echeance, supprimer_modalite, supprimer_modalite_cantine, supprimer_modalite_transport, supprimer_mois, transport_non_payees

urlpatterns = [
    path("admin/", admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/direction/', dashboard_direction, name='dashboard_direction'),
    path('dashboard/secretariat/', dashboard_tresorerie, name='dashboard_tresorerie'),
    path('dashboard/systeme/administrateur', dashboard_administrateur, name='dashboard_administrateur'),
    path('frontoffice/no_access/', no_access, name='accueil'),
    path('backoffice/no_access/', no_access_back, name='accueil_back'),
    path('backoffice/historique_connexions/', historique_connexions, name='historique_connexions'),
    
    # CORES ==============================================================================
    path('backoffice/systeme/cycles/', liste_cycles, name='liste_cycles'),
    path('cycles/ajouter/', ajouter_cycle, name='ajouter_cycle'),
    path('cycles/modifier/<int:pk>/', modifier_cycle, name='modifier_cycle'),
    path('cycles/supprimer/<int:pk>/', supprimer_cycle, name='supprimer_cycle'),
    
    path('backoffice/systeme/annees_scolaires/', liste_annees_scolaires, name='liste_annees_scolaires'),
    path('backoffice/annees_scolaires/ajouter/', ajouter_annee_scolaire, name='ajouter_annee_scolaire'),
    path('backoffice/annees_scolaires/<int:pk>/modifier/', modifier_annee_scolaire, name='modifier_annee_scolaire'),
    path('backoffice/annees_scolaires/<int:pk>/supprimer/', supprimer_annee_scolaire, name='supprimer_annee_scolaire'),
    path('backoffice/annees_scolaires/<int:pk>/generer_trimestres/', generer_trimestres, name='generer_trimestres'),
    path('backoffice/annees_scolaires/<int:pk>/activer/', activer_annee_scolaire, name='activer_annee_scolaire'),
    
    path('backoffice/trimestres/', liste_trimestres, name='liste_trimestres'),
    path('backoffice/trimestres/ajouter/', ajouter_trimestre, name='ajouter_trimestre'),
    path('backoffice/trimestres/<int:pk>/modifier/', modifier_trimestre, name='modifier_trimestre'),
    path('backoffice/trimestres/<int:pk>/supprimer/', supprimer_trimestre, name='supprimer_trimestre'),

    path('backoffice/periodes/', liste_periodes, name='liste_periodes'),
    path('backoffice/periodes/ajouter/', ajouter_periode, name='ajouter_periode'),
    path('backoffice/periodes/<int:pk>/modifier/', modifier_periode, name='modifier_periode'),
    path('backoffice/periodes/<int:pk>/supprimer/', supprimer_periode, name='supprimer_periode'),
    
    # AUTHENTIFICATIONS ==============================================================================
    # Rôles
    path('backoffice/roles/systeme/', liste_roles, name='liste_roles'),
    path('backoffice/roles/ajouter/systeme/', creer_role, name='creer_role'),
    path('backoffice/roles/<int:pk>/modifier/systeme/', modifier_role, name='modifier_role'),
    path('backoffice/roles/<int:pk>/supprimer/systeme/', supprimer_role, name='supprimer_role'),
    path('backoffice/roles/<int:role_id>/acces/systeme/', gestion_acces_role, name='gestion_acces_role'),
       
    path('maj-acces/', maj_acces_ajax, name='maj_acces_ajax'),
    
    # Utilisateurs
    path('backoffice/utilisateurs/systeme/', liste_utilisateurs, name='liste_utilisateurs'),
    path('utilisateurs/ajouter/', ajouter_utilisateur, name='ajouter_utilisateur'),
    path('backoffice/utilisateurs/modifier/<int:pk>/', modifier_utilisateur, name='modifier_utilisateur'),
    path('utilisateurs/pwd/modifier/<int:pk>/', modifier_utilisateur_pwd, name='modifier_utilisateur_pwd'),
    path('utilisateurs/supprimer/<int:pk>/', supprimer_utilisateur, name='supprimer_utilisateur'),
    path('utilisateur/<int:user_id>/basculer/', basculer_activation_utilisateur, name='basculer_utilisateur'),
    path('backoffice/utilisateurs/secretariat/', liste_utilisateurs_secretariat, name='liste_utilisateurs_secretariat'),
    path('backoffice/utilisateurs/secretariat/modifier/<int:pk>/', modifier_utilisateur_secre, name='modifier_utilisateur_secre'),
    path('backoffice/utilisateurs/etablissement/', liste_utilisateurs_etablissement, name='liste_utilisateurs_etablissement'),
    path('backoffice/utilisateurs/etablissement/modifier/<int:pk>/', modifier_utilisateur_direc, name='modifier_utilisateur_direc'),
    path('backoffice/utilisateurs/etablissement/personnels/', liste_utilisateurs_personnel, name='liste_utilisateurs_personnel'),
    path('backoffice/utilisateurs/etablissement/personnels/modifier/<int:pk>/', modifier_utilisateur_pers, name='modifier_utilisateur_pers'),
    path('backoffice/utilisateurs/economat/', liste_utilisateurs_economat, name='liste_utilisateurs_economat'),
    path('backoffice/utilisateurs/economat/modifier/<int:pk>/', modifier_utilisateur_econo, name='modifier_utilisateur_econo'),
    path('backoffice/utilisateurs/parent/', liste_utilisateurs_parent, name='liste_utilisateurs_parent'),
    path('backoffice/utilisateurs/parent/modifier/<int:pk>/', modifier_utilisateur_pare, name='modifier_utilisateur_pare'),

    # Accès fonctionnalités
    path('backoffice/acces/systeme/', liste_acces, name='liste_acces'),
    
    path('backoffice/acces/secretariat/acces/', liste_acces_secretariat, name='liste_acces_secretariat'),
    path('backoffice/acces/etablissement/acces/', liste_acces_etablissement, name='liste_acces_etablissement'),
    path('backoffice/acces/etablissement/personnels/acces/', liste_acces_personnels, name='liste_acces_personnels'),
    path('backoffice/acces/economat/acces/', liste_acces_economat, name='liste_acces_economat'),
    path('backoffice/acces/parent/acces/', liste_acces_parent, name='liste_acces_parent'),
    
    path('backoffice/acces/ajouter/systeme/', creer_acces, name='creer_acces'),
    
    # ETABLISSEMENTS ==============================================================================
    path('backoffice/etablissements/', liste_etablissements, name='liste_etablissements'),
    path('backoffice/etablissements/cycles/', etablissements_par_cycle, name='etablissements_par_cycle'),
    path('backoffice/etablissements/ajouter/', creer_etablissement, name='creer_etablissement'),
    path('backoffice/etablissements/<int:etablissement_id>/', detail_etablissement, name='detail_etablissement'),
    path('backoffice/etablissements/<int:pk>/modifier/', modifier_etablissement, name='modifier_etablissement'),
    path('backoffice/etablissements/<int:pk>/supprimer/', supprimer_etablissement, name='supprimer_etablissement'),
    path('backoffice/etablissements/<int:etablissement_id>/classes/ajouter/', creer_classe, name='ajouter_classe_etablissement'),
    path('backoffice/etablissements/<int:etablissement_id>/classes/', classes_etablissement, name='classes_par_etablissement'),
    path('backoffice/etablissements/<int:etablissement_id>/niveaux/modalites/', afficher_niveaux_et_modalites, name='afficher_niveaux_et_modalites'),
    path('backoffice/etablissement/<int:etab_id>/cantine/', modalites_cantine, name='modalites_cantine'),
    path('backoffice/etablissement/<int:etab_id>/cantine/ajouter/', ajouter_modalite_cantine, name='ajouter_modalite_cantine'),
    path('backoffice/etablissement/cantine/modifier/<int:id>/', modifier_modalite_cantine, name='modifier_modalite_cantine'),
    path('backoffice/etablissement/cantine/supprimer/<int:id>/', supprimer_modalite_cantine, name='supprimer_modalite_cantine'),
    path('backoffice/etablissement/<int:etab_id>/transport/', modalites_transport, name='modalites_transport'),
    path('backoffice/etablissement/<int:etab_id>/transport/ajouter/', ajouter_modalite_transport, name='ajouter_modalite_transport'),
    path('backoffice/etablissement/transport/modifier/<int:id>/', modifier_modalite_transport, name='modifier_modalite_transport'),
    path('backoffice/etablissement/transport/supprimer/<int:id>/', supprimer_modalite_transport, name='supprimer_modalite_transport'),
    
    path('backoffice/etablissement/type/', liste_typeetablissement, name='liste_typeetablissement'),
    path('backoffice/etablissement/type/creer/', creer_typeetablissement, name='creer_typeetablissement'),
    path('backoffice/etablissement/type/modifier/<int:pk>/', modifier_typeetablissement, name='modifier_typeetablissement'),
    path('backoffice/etablissement/type/supprimer/<int:pk>/', supprimer_typeetablissement, name='supprimer_typeetablissement'),

    
    path('backoffice/etablissement/niveaux/syteme/', liste_niveaux, name='liste_niveaux'),
    path('backoffice/etablissement/niveaux/ajouter/syteme/', creer_niveau, name='creer_niveau'),
    path('backoffice/etablissement/niveaux/<int:pk>/modifier/syteme/', modifier_niveau, name='modifier_niveau'),
    path('backoffice/etablissement/niveaux/<int:pk>/supprimer/syteme/', supprimer_niveau, name='supprimer_niveau'),
    
    path('classes/', liste_classes, name='liste_classes'),
    path('classes/<int:pk>/modifier/', modifier_classe, name='modifier_classe'),
    path('classes/<int:pk>/supprimer/', supprimer_classe, name='supprimer_classe'),
    path('classes/<int:classe_id>/emploi-temps/ajouter/', creer_emploi_temps, name='creer_emploi_temps'),
    path('classes/<int:classe_id>/emploi-temps', calendrier_emploi_classe, name='calendrier_emploi_classe'),
    
    path('emplois/', liste_emploi, name='liste_emplois'),
    path('emplois/modifier/<int:pk>/', modifier_emploi, name='modifier_emploi'),
    path('emplois/supprimer/<int:pk>/', supprimer_emploi, name='supprimer_emploi'),
    

    # MATIERES ==============================================================================
    path('backoffice/etablissement/matieres/', liste_matieres, name='liste_matieres'),
    path('matieres/ajouter/', creer_matiere, name='creer_matiere'),
    path('matieres/modifier/<int:pk>/', modifier_matiere, name='modifier_matiere'),
    path('matieres/supprimer/<int:pk>/', supprimer_matiere, name='supprimer_matiere'),
    path('matieres/<int:matiere_id>/ajouter-coefficient/', ajouter_coefficient, name='ajouter_coefficient'),
    
    path('backoffice/etablissement/coefficients/', liste_coefficients, name='liste_coefficients'),
    path('coefficients/ajouter/', creer_coefficient, name='creer_coefficient'),
    
    path('coefficients/modifier/<int:pk>/', modifier_coefficient, name='modifier_coefficient'),
    path('coefficients/supprimer/<int:pk>/', supprimer_coefficient, name='supprimer_coefficient'),
    
    path('backoffice/etablissement/coefficients_etablissement/', liste_coefficients_etablissement, name='liste_coefficients_etablissement'),
    path('coefficients_etablissement/ajouter/', creer_coefficient_etablissement, name='creer_coefficient_etablissement'),
    
    path('coefficients_periode/', liste_coefficients_periode, name='liste_coefficients_periode'),
    path('coefficients_periode/ajouter/', creer_coefficient_periode, name='creer_coefficient_periode'),
    
    
    
    # ENSEIGNANTS ==============================================================================
    path('backoffice/postes/', liste_postes, name='liste_postes'),
    path('backoffice/postes/nouveau/', creer_poste, name='creer_poste'),
    path('backoffice/postes/<int:pk>/modifier/', modifier_poste, name='modifier_poste'),
    path('backoffice/postes/<int:pk>/supprimer/', supprimer_poste, name='supprimer_poste'),
    
    
    path('backoffice/personnels/', liste_personnels, name='liste_personnels'),
    path('backoffice/secretariat/personnels/', liste_personnels_secretariat, name='liste_personnels_secretariat'),
    path('backoffice/etablissement/personnels/', liste_personnels_etablissement, name='liste_personnels_etablissement'),
    path('backoffice/economat/personnels/', liste_personnels_economat, name='liste_personnels_economat'),
    path('backoffice/instituteurs/personnels/', liste_personnels_instituteurs, name='liste_personnels_instituteurs'),
    path('backoffice/professeurs/personnels/', liste_personnels_professeurs, name='liste_personnels_professeurs'),
    path('backoffice/personnels/ajouter/', creer_personnel, name='creer_personnel'),
    path('backoffice/secretariat/personnels/ajouter/', creer_personnel_secretariat, name='creer_personnel_secretariat'),
    path('backoffice/etablissement/personnels/ajouter/', creer_personnel_direction, name='creer_personnel_direction'),
    path('backoffice/economat/personnels/ajouter/', creer_personnel_economat, name='creer_personnel_economat'),
    path('backoffice/instituteurs/personnels/ajouter/', creer_personnel_adjoint, name='creer_personnel_adjoint'),
    path('backoffice/professeurs/personnels/ajouter/', creer_personnel_professeur, name='creer_personnel_professeur'),
    path('backoffice/personnels/<int:pk>/modifier/', modifier_personnel, name='modifier_personnel'),
    path('backoffice/secretariat/personnels/<int:pk>/modifier/', modifier_personnel_secretariat, name='modifier_personnel_secretariat'),
    path('backoffice/etablissement/personnels/<int:pk>/modifier/', modifier_personnel_etablissement, name='modifier_personnel_etablissement'),
    path('backoffice/economat/personnels/<int:pk>/modifier/', modifier_personnel_economat, name='modifier_personnel_economat'),
    path('backoffice/instituteurs/personnels/<int:pk>/modifier/', modifier_personnel_adjoint, name='modifier_personnel_adjoint'),
    path('backoffice/professeurs/personnels/<int:pk>/modifier/', modifier_personnel_professeur, name='modifier_personnel_professeur'),
    path('backoffice/personnels/<int:pk>/supprimer/', supprimer_personnel, name='supprimer_personnel'),

   # MutationPersonnel
    path('mutations/', liste_mutations, name='liste_mutations'),
    path('mutations/ajouter/', ajouter_mutation, name='ajouter_mutation'),
    path('mutations/<int:pk>/modifier/', modifier_mutation, name='modifier_mutation'),
    path('mutations/<int:pk>/supprimer/', supprimer_mutation, name='supprimer_mutation'),

    # TenueDeClasse
    path('tenues/', liste_tenue_classe, name='liste_tenue_classe'),
    path('tenues/ajouter/', ajouter_tenue_classe, name='ajouter_tenue_classe'),
    path('tenues/<int:pk>/modifier/', modifier_tenue_classe, name='modifier_tenue_classe'),
    path('tenues/<int:pk>/supprimer/', supprimer_tenue_classe, name='supprimer_tenue_classe'),

    # Affectation
    path('affectations/', liste_affectations, name='liste_affectations'),
    path('affectations/ajouter/', ajouter_affectation, name='ajouter_affectation'),
    path('affectations/<int:pk>/modifier/', modifier_affectation, name='modifier_affectation'),
    path('affectations/<int:pk>/supprimer/', supprimer_affectation, name='supprimer_affectation'),


    # SCOLARITES ==============================================================================
    # Modalités
    path('modalites/', liste_modalites, name='liste_modalites'),
    path('modalites/ajouter/', creer_modalite, name='ajouter_modalite'),
    path('modalites/modifier/<int:pk>/', modifier_modalite, name='modifier_modalite'),
    path('modalites/supprimer/<int:pk>/', supprimer_modalite, name='supprimer_modalite'),
    path('modalites/<int:pk>/', detail_modalite, name='detail_modalite'),
    path('modalites/<int:modalite_id>/ajouter-echeance/', ajouter_echeance, name='ajouter_echeance'),
    path('backoffice/etablissements/modalites/<int:modalite_id>/modifier-echeances/', modifier_echeances_modalite, name='modifier_echeances_modalite'),
    path('backoffice/etablissements/<int:etablissement_id>/modalites/', liste_modalites_etablissement_back, name='liste_modalites_etablissement_back'),
    path('backoffice/etablissements/modalites/<int:modalite_id>/echeances/', detail_echeances_modalite_back, name='detail_echeances_modalite_back'),  # à créer
    path('backoffice/mois/', liste_mois, name='liste_mois'),
    path('backoffice/mois/creer/', creer_mois, name='creer_mois'),
    path('backoffice/mois/modifier/<int:pk>/', modifier_mois, name='modifier_mois'),
    path('backoffice/mois/supprimer/<int:pk>/', supprimer_mois, name='supprimer_mois'),
    
    # Échéances
    path('echeances/', liste_echeances, name='liste_echeances'),
    path('echeances/ajouter/', creer_echeance, name='ajouter_echeance'),
    path('echeances/modifier/<int:pk>/', modifier_echeance, name='modifier_echeance'),
    path('echeances/supprimer/<int:pk>/', supprimer_echeance, name='supprimer_echeance'),
    

    # ELEVES ==============================================================================
    path('backoffice/eleves/importer/', import_eleves_back, name='import_eleves_back'),
    path('backoffice/eleves/ajouter/', ajouter_eleve_back, name='ajouter_eleve_back'),
    path('backoffice/secretariat/eleves/', liste_eleves_back, name='liste_eleves_back'),
    path('backoffice/secretariat/parents/liens/', liste_liens_back, name='liste_liens_back'),
    
    path('frontoffice/eleves/muter_eleves/', muter_eleves, name='muter_eleves'),


    #path('backoffice/secretariat/eleves/', liste_eleves, name='liste_eleves'),
    path('backoffice/eleves/systeme', liste_eleves_systeme, name='liste_eleves_systeme'),
    path('backoffice/secretariat/eleves/ajouter/', ajouter_eleve, name='ajouter_eleve'),
    path('eleves/<int:eleve_id>/modifier/', modifier_eleve, name='modifier_eleve'),
    path('eleves/<int:eleve_id>/supprimer/', supprimer_eleve, name='supprimer_eleve'),
    path('backoffice/eleves/importer/', import_eleves, name='import_eleves'),
    
    
    
    path('liens/', liste_liens, name='liste_liens'),
    path('liens/ajouter/', ajouter_lien, name='ajouter_lien'),
    path('liens/<int:pk>/modifier/', modifier_lien, name='modifier_lien'),
    path('liens/<int:pk>/supprimer/', supprimer_lien, name='supprimer_lien'),
    
    # Inscription --------------------------------------------
    path('traitement-matricule/', traitement_matricule, name='traitement_matricule'),
    path('paiements/<int:eleve_id>/', detail_paiement, name='detail_paiement'),
    path('inscriptions/ajouter/<int:eleve_id>/', ajouter_inscription, name='ajouter_inscription'),
    path('eleves/ajouter/', ajouter_eleveprerempli, name='ajouter_eleveprerempli'),
    path('paiement/recu/<int:inscription_id>/', recu_paiement_pdf, name='recu_paiement_pdf'),
    

    
    # SCOLARITE ==============================================================================
    path('frontoffice/paiements/ajouter/<int:inscription_id>/', ajouter_paiement, name='ajouter_paiement'),
    path('frontoffice/paiements/cantine/paiement/<int:eleve_id>/', cantine_non_payees, name='cantine_paiement'),
    path('frontoffice/paiements/transport/paiement/<int:eleve_id>/', transport_non_payees, name='transport_paiement'),


    # RAPPORTS ==============================================================================
    path('backoffice/rapports/tableau/', tableau_relances_par_etablissement, name='tableau_relances'),
    path('backoffice/rapports/export/relances/excel/', rapport_export_relances_excel, name='rapport_export_relances_excel'),
    path('backoffice/rapports/export/relances/pdf/', rapport_export_relances_pdf, name='rapport_export_relances_pdf'),
  
    path('backoffice/rapport/secretariat/primaire/effectif/', effectif_par_niveau_genre, name='effectif_par_niveau_genre'),
    path('backoffice/rapports/secretariat/primaire/effectif/export/excel/', export_effectif_excel, name='export_effectif_excel'),
    path('backoffice/rapports/secretariat/primaire/effectif/export/pdf/', export_effectif_pdf, name='export_effectif_pdf'),
    path('backoffice/rapport/secretariat/secondaire/effectif/', effectif_par_niveau_genre_sec, name='effectif_par_niveau_genre_sec'),
    path('backoffice/rapports/secretariat/secondaire/effectif/export/excel/', export_effectif_excel_sec, name='export_effectif_excel_sec'),
    path('backoffice/rapports/secretariat/secondaire/effectif/export/pdf/', export_effectif_pdf_sec, name='export_effectif_pdf_sec'),
    path('backoffice/rapports/secretariat/etatscolarite/', tableau_etatscolarite_par_etablissement_secretariat, name='tableau_etatscolarite_par_etablissement_secretariat'),
    path('backoffice/rapports/secretariat/etatscolarite/export/excel/', rapport_export_etatscolarite_secretariat_excel, name='rapport_export_etatscolarite_secretariat_excel'),
    path('backoffice/rapports/secretariat/etatscolarite/export/pdf/', rapport_export_etatscolarite_secretariat_pdf, name='rapport_export_etatscolarite_secretariat_pdf'),
    path('backoffice/rapports/secretariat/effectif/abandons/', effectif_par_niveau_genre_abandon_tous_etablissements, name='effectif_par_niveau_genre_abandon_tous_etablissements'),
    path('backoffice/rapports/secretariat/effectif/abandons/export/excel/', export_effectif_abandon_global_excel, name='export_effectif_abandon_global_excel'),
    path('backoffice/rapports/secretariat/effectif/abandons/export/pdf/', export_effectif_abandon_global_pdf, name='export_effectif_abandon_global_pdf'),
    path('backoffice/rapports/etatscolarite/abandons/', tableau_etatscolarite_pour_secretariat_classe_abandons, name='tableau_etatscolarite_pour_secretariat_classe_abandons'),
    path('backoffice/rapports/etatscolarite/presents/', tableau_etatscolarite_pour_secretariat_classe_presents, name='tableau_etatscolarite_pour_secretariat_classe_presents'),
    path('backoffice/rapports/eleves-inscrits/abandons/', eleves_inscrits_abandon_tous, name='eleves_inscrits_abandon_tous'),
    path('backoffice/rapports/export/eleves_abandons/excel/', export_eleves_inscrits_abandon_tous_excel, name='export_eleves_inscrits_abandon_tous_excel'),
    path('backoffice/rapports/export/eleves_abandons/pdf/', export_eleves_inscrits_abandon_tous_pdf, name='export_eleves_inscrits_abandon_tous_pdf'),
    path('backoffice/rapports/eleves-inscrits/reductions/', eleves_inscrits_reduction_tous, name='eleves_inscrits_reduction_tous'),
    path('backoffice/rapports/export/eleves_reductions/excel/', export_eleves_inscrits_reduction_tous_excel, name='export_eleves_inscrits_reduction_tous_excel'),
    path('backoffice/rapports/export/eleves_reductions/pdf/', export_eleves_inscrits_reduction_tous_pdf, name='export_eleves_inscrits_reduction_tous_pdf'),
    path('backoffice/rapports/etatscolarite/affecte/', tableau_etatscolarite_affecte_par_secretariat, name='tableau_etatscolarite_affecte_par_secretariat'),
    path('backoffice/rapports/etatscolarite/nonaffecte/', tableau_etatscolarite_nonaffecte_par_secretariat, name='tableau_etatscolarite_nonaffecte_par_secretariat'),
    path('backoffice/rapports/etatscolarite/affecte/export/excel/', rapport_export_etatscolarite_secretariat_affecte_excel, name='rapport_export_etatscolarite_secretariat_affecte_excel'),
    path('backoffice/rapports/etatscolarite/affecte/export/pdf/', rapport_export_etatscolarite_secretariat_affecte_pdf, name='rapport_export_etatscolarite_secretariat_affecte_pdf'),
    path('backoffice/rapports/etatscolarite/nonaffecte/export/excel/', rapport_export_etatscolarite_secretariat_nonaffecte_excel, name='rapport_export_etatscolarite_secretariat_nonaffecte_excel'),
    path('backoffice/rapports/etatscolarite/nonaffecte/export/pdf/', rapport_export_etatscolarite_secretariat_nonaffecte_pdf, name='rapport_export_etatscolarite_secretariat_nonaffecte_pdf'),

    path('backoffice/paiements/etablissement/', liste_paiements_back, name='liste_paiements_back'),
    path('backoffice/paiements/export/excel/', export_paiements_excel_back, name='export_paiements_excel_back'),
    path('backoffice/paiements/export/pdf/', export_paiements_pdf_back, name='export_paiements_pdf_back'),
    path('backoffice/paiements/transport/', liste_paiements_back_transport, name='liste_paiements_back_transport'),
    path('backoffice/paiements/transport/export/excel/', export_paiements_transport_excel_back, name='export_paiements_transport_excel_back'),
    path('backoffice/paiements/transport/export/pdf/', export_paiements_transport_pdf_back, name='export_paiements_transport_pdf_back'),
    path('backoffice/paiements/cantine/etablissement/', liste_paiements_back_cantine, name='liste_paiements_back_cantine'),
    path('backoffice/paiements/cantine/export/excel/', export_paiements_cantine_excel_back, name='export_paiements_cantine_excel_back'),
    path('backoffice/paiements/cantine/export/pdf/', export_paiements_cantine_pdf_back, name='export_paiements_cantine_pdf_back'),
    
    path('backoffice/paiements/etablissement/bilan-nature/', bilan_paiements_par_nature_back, name='bilan_par_nature_back'),
    path('backoffice/paiements/transport/etablissement/bilan-nature/', bilan_paiements_par_nature_transport_back, name='bilan_par_nature_transport_back'),
    path('backoffice/paiements/cantine/etablissement/bilan-nature/', bilan_paiements_par_nature_cantine_back, name='bilan_par_nature_cantine_back'),

    path('backoffice/paiements/arrieres/etablissement/', liste_paiements_arrieres_back, name='liste_paiements_arrieres_back'),
    path('backoffice/paiements/arrieres/export/excel/', export_paiements_arrieres_excel_back, name='export_paiements_arrieres_excel_back'),
    path('backoffice/paiements/arrieres/export/pdf/', export_paiements_arrieres_pdf_back, name='export_paiements_arrieres_pdf_back'),
    
    path('backoffice/etablissement/echeances/groupes/', liste_echeances_groupes, name='echeances_groupes'),
    path('backoffice/etablissement/relances/non-a-jour/', liste_relances_non_a_jour, name='relances_non_a_jour'),
    path('backoffice/etablissement/relances/pdf/', export_relances_pdf, name='export_relances_pdf'),
    path('backoffice/etablissement/relances/excel/', export_relances_excel, name='export_relances_excel'),
    
    path('backoffice/etablissement/classe/relances/tous/non-a-jour/', liste_relances_secretariat_non_a_jour, name='liste_relances_secretariat_non_a_jour'),
    path('backoffice/etablissement/classe/relances/tous/relances/envoyer-sms/', envoyer_sms_relances, name='envoyer_sms_relances'),

    path('backoffice/etablissement/classe/relances/tous/pdf/', export_relances_secretariat_pdf, name='export_relances_secretariat_pdf'),
    path('backoffice/etablissement/classe/relances/tous/excel/', export_relances_secretariat_excel, name='export_relances_secretariat_excel'),
    
    
    
    
    # CAISSES ==============================================================================
    # Caisses
    path('backoffice/caisses/', liste_caisses, name='liste_caisses'),
    path('backoffice/caisses/ajouter/', ajouter_caisse, name='ajouter_caisse'),
    path('backoffice/caisses/<int:caisse_id>/detail/', detail_caisse, name='detail_caisse'),
    path('backoffice/caisses/<int:caisse_id>/depenses/enattente/', liste_depenses_caisse, name='liste_depenses_caisse'),
    path('backoffice/caisses/modifier/<int:pk>/',modifier_caisse, name='modifier_caisse'),
    path('backoffice/caisses/supprimer/<int:pk>/', supprimer_caisse, name='supprimer_caisse'),
    
    path('backoffice/caisses/depenses/modifier/<int:depense_id>/', modifier_depense_back, name='modifier_depense_back'),
    
    # Caisse principale
    path('backoffice/caisses/principale/detail/', detail_caisse_principale, name='detail_caisse_principale'),
    path('backoffice/caisses/principale/<int:caisse_id>/point/', liste_operations_points, name='liste_operations_points'),
    path('backoffice/caisses/principale/<int:caisse_id>/point/export/excel/', export_operations_excel, name='export_operations_excel'),
    path('backoffice/caisses/principale/<int:caisse_id>/point/export/pdf/', export_operations_pdf, name='export_operations_pdf'),
    
    path('backoffice/caisses/<int:caisse_id>/operations/', liste_operations, name='liste_operations'),
    path('backoffice/caisses/<int:caisse_id>/operations/ajouter/', ajouter_operation, name='ajouter_operation'),
    path('backoffice/operations/<int:id>/modifier/', modifier_operation, name='modifier_operation'),
    path('backoffice/operations/<int:id>/supprimer/', supprimer_operation, name='supprimer_operation'),

    path('backoffice/operations/caisseetablissement/<int:caisse_id>/enregistrer-dotation/', enregistrer_dotation, name='enregistrer_dotation'),

    # Depenses
    path('frontoffice/<int:etablissement_id>/caisses/', liste_caisses_etablissement, name='liste_caisses_etablissement'),
    path('frontoffice/depenses/', liste_depenses, name='liste_depenses'),
    path('frontoffice/depenses/<int:caisse_id>/ajouter/', ajouter_depense, name='ajouter_depense'),
    path('frontoffice/depenses/modifier/<int:pk>/', modifier_depense, name='modifier_depense'),
    path('frontoffice/depenses/supprimer/<int:pk>/', supprimer_depense, name='supprimer_depense'),
    
    # NOTES ==============================================================================
    path('backoffice/notes/type-evaluation/', liste_type_evaluations, name='liste_type_evaluations'),
    path('backoffice/notes/type-evaluation/creer/', creer_type_evaluation, name='creer_type_evaluation'),
    path('backoffice/notes/type-evaluation/modifier/<int:pk>/', modifier_type_evaluation, name='modifier_type_evaluation'),
    path('backoffice/notes/type-evaluation/supprimer/<int:pk>/', supprimer_type_evaluation, name='supprimer_type_evaluation'),
    
    # CORES ==============================================================================
    # CORES ==============================================================================
    # CORES ==============================================================================
    # ESPACE PARENT ==============================================================================
    
    path('educationcatholique/espaceparent/', espace_parent, name='espace_parent'),
    path('educationcatholique/espaceparent/parent/eleve/<str:matricule>/', detail_eleve_parent, name='detail_eleve_parent'),
    path('educationcatholique/espaceparent/dashboard/', dashboard_parent, name='dashboard'),
    path('educationcatholique/espaceparent/mes-enfants/', liste_enfants, name='mes_enfants'),
    path('educationcatholique/espaceparent/fiche-eleve/<int:eleve_id>/',fiche_eleve, name='fiche_eleve'),
    path('educationcatholique/espaceparent/parent/paiements/', paiements_eleve, name='paiements_eleve'),
    path('educationcatholique/espaceparent/parent/bulletins/', bulletins_eleve, name='bulletins_eleve'),
    path('educationcatholique/espaceparent/parent/paiements/ajouter/<int:inscription_id>/', ajouter_paiement_parent, name='ajouter_paiement_parent'),
    
    path('cinetpay/notify/', cinetpay_notify, name='cinetpay_notify'),
    #path('api/cinetpay/init/', init_cinetpay, name='init_cinetpay'),init_cinetpay_view
    path('api/cinetpay/init/', init_cinetpay_view, name='init_cinetpay'),

    
    
    # FRONT OFFICE =======================================================================================================================================
    # Front liste etablissement --------------------------------------------
    path('frontoffice/eleves/base', liste_eleves_etablissement, name='liste_eleves_etablissement'),
    path('frontoffice/eleves/base/start/', liste_eleves_etablissement_start, name='liste_eleves_etablissement_start'),
    path('frontoffice/eleves/ajouter/', ajouter_eleve_etablissement, name='ajouter_eleve_etablissement'),
    path('frontoffice/eleves/<str:matricule>/', detail_eleve, name='detail_eleve'),
    path('frontoffice/eleves-inscrits/', eleves_inscrits_etablissement, name='liste_eleves_inscrits'),
    path('frontoffice/eleves-inscrits/abandons/', eleves_inscrits_abandon_etablissement, name='eleves_inscrits_abandon_etablissement'),
    path('frontoffice/eleves-inscrits/abandons/export/excel/', export_eleves_inscrits_abandon_excel, name='export_eleves_inscrits_abandon_excel'),
    path('frontoffice/eleves-inscrits/abandons/export/pdf/', export_eleves_inscrits_abandon_pdf, name='export_eleves_inscrits_abandon_pdf'),
    path('frontoffice/eleves-inscrits/reductions/export/excel/', export_eleves_inscrits_reduction_excel, name='export_eleves_inscrits_reduction_excel'),
    path('frontoffice/eleves-inscrits/reductions/export/pdf/', export_eleves_inscrits_reduction_pdf, name='export_eleves_inscrits_reduction_pdf'),
    path('frontoffice/eleves-inscrits/reductions/', eleves_inscrits_reduction_etablissement, name='eleves_inscrits_reduction_etablissement'),
    path('frontoffice/eleves-inscrits/export/excel/', export_eleves_inscrits_excel, name='export_eleves_inscrits_excel'),
    path('frontoffice/eleves-inscrits/export/pdf/', export_eleves_inscrits_pdf, name='export_eleves_inscrits_pdf'),
    path('frontoffice/classes-avec-inscrits/', classes_avec_eleves_inscrits, name='classes_avec_inscrits'),
    path('frontoffice/eleves-inscrits/classe/<int:classe_id>/', liste_eleves_inscrits_par_classe, name='liste_eleves_inscrits_par_classe'),
    path('frontoffice/relances/<str:statut>/', liste_relances, name='liste_relances'),
    
    path('frontoffice/matieres/', liste_matieres_etablissements, name='liste_matieres_etablissements'),
    path('frontoffice/matieres/ajouter/<int:cycle_id>/', ajouter_matiere, name='ajouter_matiere'),
    
    path('get-professeurs/', get_professeurs_par_matiere, name='get_professeurs'),
    path('frontoffice/classes/cyclecollege/<int:classe_id>/emploi-temps/ajouter/', creer_emploi_temps, name='creer_emploi_temps'),
    path('frontoffice/classes/cycleprimaire/<int:classe_id>/emploi-temps/ajouter/', creer_emploi_temps_primaire, name='creer_emploi_temps_primaire'),
    path('frontoffice/classes/<int:classe_id>/emploi-temps', calendrier_emploi_classe, name='calendrier_emploi_classe'),
    path('frontoffice/etablissement/<int:etablissement_id>/emplois/pdf/', emploi_temps_etablissement_pdf, name='emplois_etablissement_pdf'),
    path('frontoffice/etablissement/classe/<int:classe_id>/emploi-temps/pdf/', emploi_temps_pdf, name='emploi_temps_pdf'),
    path('frontoffice/classes/emplois/modifier/<int:pk>/', modifier_emploi, name='modifier_emploi'),
    path('frontoffice/classes/emplois/cycleprimaire/modifier/<int:pk>/', modifier_emploi_primaire, name='modifier_emploi_primaire'),
    path('frontoffice/classes/emplois/supprimer/<int:pk>/', supprimer_emploi, name='supprimer_emploi'),
    
    path('frontoffice/classes/notes/selection/<int:classe_id>/', selectionner_matiere_periode, name='selectionner_matiere_periode'),
    path('frontoffice/classes/notes/ajouter/<int:classe_id>/<int:matiere_id>/<int:periode_id>/', ajouter_notes_classe, name='ajouter_notes_classe'),
    path('frontoffice/classes/notes/modifier/<int:classe_id>/<int:matiere_id>/<int:periode_id>/', modifier_notes_classe, name='modifier_notes_classe'),
    path('frontoffice/classes/notes/voir/<int:classe_id>/<int:matiere_id>/<int:periode_id>/', voir_notes_classe, name='voir_notes_classe'),

    path('frontoffice/etablissement/paiements/<int:eleve_id>/', detail_paiement, name='detail_paiement'),
    
    path('frontoffice/etablissement/echeances/groupes/', liste_echeances_groupes, name='echeances_groupes'),
    path('frontoffice/etablissement/relances/non-a-jour/', liste_relances_non_a_jour, name='relances_non_a_jour'),
    path('frontoffice/etablissement/relances/pdf/', export_relances_pdf, name='export_relances_pdf'),
    path('frontoffice/etablissement/relances/excel/', export_relances_excel, name='export_relances_excel'),
    
    path('frontoffice/etablissement/classe/relances/<int:classe_id>/non-a-jour/', liste_relances_classe_non_a_jour, name='relances_classe_non_a_jour'),
    path('frontoffice/etablissement/classe/relances/<int:classe_id>/pdf/', export_relances_classe_pdf, name='export_relances_classe_pdf'),
    path('frontoffice/etablissement/classe/relances/<int:classe_id>/excel/', export_relances_classe_excel, name='export_relances_classe_excel'),
    
    path('frontoffice/etablissement/<int:etablissement_id>/classes/ajouter/', creer_classe_etablissement, name='ajouter_classe_etablissement_etablissement'),
    path('frontoffice/etablissement/classes/<int:pk>/modifier/', modifier_classe_etablissement, name='modifier_classe_etablissement'),
    
    path('frontoffice/rapports/effectif/', effectif_par_niveau_genre_etablissement, name='effectif_par_niveau_genre_etablissement'),
    path('frontoffice/rapports/effectif/export/excel/', export_effectif_excel_etablissement, name='export_effectif_excel_etablissement'),
    path('frontoffice/rapports/effectif/export/pdf/', export_effectif_pdf_etablissement, name='export_effectif_pdf_etablissement'),
    path('frontoffice/rapports/effectif/abandons/', effectif_par_niveau_genre_abandon_etablissement, name='effectif_par_niveau_genre_abandon_etablissement'),
    path('frontoffice/rapports/effectif/abandons/export/excel/', export_effectif_excel_etablissement_abandon, name='export_effectif_excel_etablissement_abandon'),
    path('frontoffice/rapports/effectif/abandons/export/pdf/', export_effectif_pdf_etablissement_abandon, name='export_effectif_pdf_etablissement_abandon'),
    path('frontoffice/rapports/etatscolarite/', tableau_etatscolarite_pour_etablissement_classe, name='tableau_etatscolarite_pour_etablissement_classe'),
    path('frontoffice/rapports/etatscolarite/abandons/', tableau_etatscolarite_pour_etablissement_classe_abandons, name='tableau_etatscolarite_pour_etablissement_classe_abandons'),
    path('frontoffice/rapports/etatscolarite/presents/', tableau_etatscolarite_pour_etablissement_classe_presents, name='tableau_etatscolarite_pour_etablissement_classe_presents'),
    path('frontoffice/rapports/etatscolarite/affecte/', tableau_etatscolarite_pour_etablissement_classe_affecte, name='tableau_etatscolarite_pour_etablissement_classe_affecte'),
    path('frontoffice/rapports/etatscolarite/nonaffecte/', tableau_etatscolarite_pour_etablissement_classe_nonaffecte, name='tableau_etatscolarite_pour_etablissement_classe_nonaffecte'),
    path('frontoffice/rapports/etatscolarite/export/excel/', rapport_export_etatscolarite_classe_excel, name='rapport_export_etatscolarite_classe_excel'),
    path('frontoffice/rapports/etatscolarite/export/pdf/', rapport_export_etatscolarite_classe_pdf, name='rapport_export_etatscolarite_classe_pdf'),
    path('frontoffice/rapports/etatscolarite/affecte/export/excel/', rapport_export_etatscolarite_classe_affecte_excel, name='rapport_export_etatscolarite_classe_affecte_excel'),
    path('frontoffice/rapports/etatscolarite/affecte/export/pdf/', rapport_export_etatscolarite_classe_affecte_pdf, name='rapport_export_etatscolarite_classe_affecte_pdf'),
    path('frontoffice/rapports/etatscolarite/nonaffecte/export/excel/', rapport_export_etatscolarite_classe_non_affecte_excel, name='rapport_export_etatscolarite_classe_non_affecte_excel'),
    path('frontoffice/rapports/etatscolarite/nonaffecte/export/pdf/', rapport_export_etatscolarite_classe_non_affecte_pdf, name='rapport_export_etatscolarite_classe_non_affecte_pdf'),
    
    path('frontoffice/personnels/enseignants/ajouter/', creer_personnel_etablissement, name='creer_personnel_etablissement'),
    path('frontoffice/enseignants/', liste_enseignants, name='liste_enseignants'),
    path('frontoffice/enseignants/tenue/ajouter/<int:enseignant_id>/', ajouter_tenue_de_classe, name='ajouter_tenue_de_classe'),
    path('frontoffice/enseignants/export/excel/', export_enseignants_excel, name='export_enseignants_excel'),
    path('frontoffice/enseignants/export/pdf/', export_enseignants_pdf, name='export_enseignants_pdf'),
    
    path('frontoffice/paiements/etablissement/', liste_paiements_etablissement, name='liste_paiements_etablissement'),
    path('frontoffice/paiements/export/excel/', export_paiements_excel, name='export_paiements_excel'),
    path('frontoffice/paiements/export/pdf/', export_paiements_pdf, name='export_paiements_pdf'),
    path('frontoffice/paiements/transport/etablissement/', liste_paiements_etablissement_transport, name='liste_paiements_etablissement_transport'),
    path('frontoffice/paiements/transport/export/excel/', export_paiements_transport_excel, name='export_paiements_transport_excel'),
    path('frontoffice/paiements/transport/export/pdf/', export_paiements_transport_pdf, name='export_paiements_transport_pdf'),
    path('frontoffice/paiements/cantine/etablissement/', liste_paiements_etablissement_cantine, name='liste_paiements_etablissement_cantine'),
    path('frontoffice/paiements/cantine/export/excel/', export_paiements_cantine_excel, name='export_paiements_cantine_excel'),
    path('frontoffice/paiements/cantine/export/pdf/', export_paiements_cantine_pdf, name='export_paiements_cantine_pdf'),
    path('frontoffice/paiements/etablissement/bilan-nature/', bilan_paiements_par_nature, name='bilan_par_nature'),
    path('frontoffice/paiements/transport/etablissement/bilan-nature/', bilan_paiements_par_nature_transport, name='bilan_par_nature_transport'),
    path('frontoffice/paiements/cantine/etablissement/bilan-nature/', bilan_paiements_par_nature_cantine, name='bilan_par_nature_cantine'),
    path('frontoffice/paiements/arrieres/etablissement/', liste_paiements_arrieres_etablissement, name='liste_paiements_arrieres_etablissement'),
    path('frontoffice/paiements/arrieres/export/excel/', export_paiements_arrieres_excel, name='export_paiements_arrieres_excel'),
    path('frontoffice/paiements/arrieres/export/pdf/', export_paiements_arrieres_pdf, name='export_paiements_arrieres_pdf'),
    
    
    
    # API ==============================================================================
    path('api-token-auth/', CustomAuthToken.as_view()),
    path('logout_userbank', logout_userbank, name='logout_userbank'),
    path('api/parent/dashboard/', ParentDashboardView.as_view()),
    path('api/parent/enfants/', EnfantsDuParentAPIView.as_view()),
    path('api/eleves/<int:eleve_id>/relances/', RelancesEleveAPIView.as_view()),
    path('api/eleves/<int:eleve_id>/cantine/non_payees/', modalites_cantine_non_payees),
    path('api/eleves/<int:eleve_id>/transport/non_payees/', modalites_transport_non_payees),
    path('api/paiements/parent/', PaiementsParTypeAPIView.as_view()),
    path('api/evenements/parent/', EvenementsParentAPIView.as_view()),
    path('api/parent/eleves/<int:id>/fiche/', api_fiche_enfants),
    
    path('api/direction/dashboard/', dashboard_direction_api),
    path('api/direction/eleves/', ListeElevesDirectionAPIView.as_view(), name='direction-eleves'),
    path('api/eleves/<str:matricule>/', eleve_par_matricule, name='eleve_par_matricule'),
    path('api/classes/', api_liste_classes_inscription, name='api_liste_classes_inscription'),
    path('api/inscription/', ajouter_inscription_api, name='api_inscription'),
    #path('api/eleves/ajouter/', ajouter_eleve_api),
    path('api/eleves/ajouter/', ajouter_eleve_api, name='ajouter_eleve_api'),
    path('api/eleves/', EleveViewSet.as_view({'post': 'create'}), name='ajouter_eleve_api-create'),
    path('api/direction/classes/', api_liste_classes),
    path('api/direction/eleves/optiondeux', api_direction_elevesoptiondeux),
    path('api/paiements/direction/', PaiementsParTypeDirectionAPIView.as_view()),
    path('api/direction/eleves/<int:id>/fiche/', api_fiche_eleve),
    path('api/direction/eleves/paiements/un', PaiementCreateView.as_view(), name='paiement-create'),
    path('api/direction/eleves/paiements/', PaiementViewSet.as_view({'post': 'create'}), name='paiement-create'),
    path('api/direction/eleves/paiements/transport/', PaiementTransportViewSet.as_view({'post': 'create'}), name='paiementtransport-create'),
    path('api/direction/eleves/paiements/cantine/', PaiementCantineViewSet.as_view({'post': 'create'}), name='paiementcantine-create'),
    path('api/direction/enseignants/', api_liste_enseignants),

    
    path('api/secretariat/dashboard/', dashboard_secretariat),
    path('api/secretariat/eleves/', api_eleves_secretariat),
    path('api/secretariat/etablissements/', api_liste_etablissements),
    path('api/secretariat/paiements/', PaiementsParTypeSecretariatAPIView.as_view()),
    path('api/secretariat/enseignants/', api_liste_enseignants_secretariat),
    
    path('api/cinetpay/notify/', cinetpay_notify, name='cinetpay_notify'),

    

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')