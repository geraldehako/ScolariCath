# views.py

from django.shortcuts import render, get_object_or_404, redirect

from authentifications.decorators import fonctionnalite_autorisee
from cores.models import AnneeScolaires
from etablissements.models import Etablissements
from .models import CaisseCentrales, Caisses, Depenses, Operations
from .forms import CaisseForm, DepenseForm, OperationForm
from django.contrib import messages
from django.db.models import Sum
from django.core.exceptions import ValidationError
# --- CAISSES ---

@fonctionnalite_autorisee('liste_caisses') 
def liste_caisses(request):
    caisses = Caisses.objects.all() 
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    return render(request, 'backoffice/caisses/liste_caisses.html', {'caisses': caisses,'annee_active': annee_active})

@fonctionnalite_autorisee('liste_caisses_etablissement')  
def liste_caisses_etablissement(request, etablissement_id):
    etablissement = get_object_or_404(Etablissements, pk=etablissement_id)
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    
    # Filtrer une seule caisse de l'établissement et de l'année scolaire active
    caisses = Caisses.objects.filter(etablissement=etablissement, annee_scolaire=annee_active).first()

    depenses = Depenses.objects.filter(caisse=caisses).order_by('-date_depense') if caisses else []
 
    
    context = {
        'etablissement': etablissement,
        'annee_active': annee_active,
        'caisses': caisses,
        'depenses': depenses,
    }
    return render(request, 'frontoffice/caisses/liste_caisses_etablissement.html', context)

@fonctionnalite_autorisee('detail_caisse') 
def detail_caisse(request, caisse_id):
    caisses = get_object_or_404(Caisses, pk=caisse_id)
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    depenses = Depenses.objects.filter(caisse=caisses).order_by('-date_depense') if caisses else []
 
    context = {
        'annee_active': annee_active,
        'caisses': caisses,
        'depenses': depenses,
    }
    return render(request, 'backoffice/caisses/detail_caisse.html', context)

@fonctionnalite_autorisee('liste_depenses_caisse') 
def liste_depenses_caisse(request, caisse_id):
    caisses = get_object_or_404(Caisses, pk=caisse_id)
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    depenses = Depenses.objects.filter(caisse=caisses,statut_validation="en_attente").order_by('-date_depense') if caisses else []
 
    context = {
        'annee_active': annee_active,
        'caisses': caisses,
        'depenses': depenses,
        'Depenses': Depenses,
    }
    return render(request, 'backoffice/caisses/liste_depenses_caisse.html', context)

@fonctionnalite_autorisee('ajouter_caisse') 
def ajouter_caisse(request):
    if request.method == 'POST':
        form = CaisseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_caisses')
    else:
        form = CaisseForm()
    return render(request, 'frontoffice/caisses/form_caisse.html', {'form': form, 'action': 'Ajouter'})

@fonctionnalite_autorisee('modifier_caisse') 
def modifier_caisse(request, pk):
    caisse = get_object_or_404(Caisses, pk=pk)
    if request.method == 'POST':
        form = CaisseForm(request.POST, instance=caisse)
        if form.is_valid():
            form.save()
            return redirect('liste_caisses')
    else:
        form = CaisseForm(instance=caisse)
    return render(request, 'frontoffice/caisses/form_caisse.html', {'form': form, 'action': 'Modifier'})

@fonctionnalite_autorisee('supprimer_caisse') 
def supprimer_caisse(request, pk):
    caisse = get_object_or_404(Caisses, pk=pk)
    if request.method == 'POST':
        caisse.delete()
        return redirect('liste_caisses')
    return render(request, 'frontoffice/caisses/confirm_delete.html', {'objet': caisse})

# --- DEPENSES ---

def liste_depenses(request):
    depenses = Depenses.objects.select_related('caisse').all()
    return render(request, 'frontoffice/depenses/liste_depenses.html', {'depenses': depenses})

from django.shortcuts import get_object_or_404
@fonctionnalite_autorisee('ajouter_depense')   
def ajouter_depense(request, caisse_id):
    caisse = get_object_or_404(Caisses, pk=caisse_id) if caisse_id != 0 else None
    annee_active = AnneeScolaires.objects.filter(active=True).first()

    if request.method == 'POST':
        form = DepenseForm(request.POST, request.FILES)
        if form.is_valid():
            depense = form.save(commit=False)
            depense.responsable = request.user
            depense.annee_scolaire = annee_active
            depense.statut_validation = 'en_attente' 
            if caisse:
                depense.caisse = caisse
            depense.save()
            return redirect('liste_caisses_etablissement', etablissement_id=caisse.etablissement.id if caisse else None)
    else:
        initial = {}
        if caisse:
            initial['caisse'] = caisse
        if annee_active:
            initial['annee_scolaire'] = annee_active
        form = DepenseForm(initial=initial)

    return render(request, 'frontoffice/depenses/form_depense.html', {'form': form, 'action': 'Ajouter'})

@fonctionnalite_autorisee('modifier_depense_back') 
def modifier_depense_back(request, depense_id):
    depense = get_object_or_404(Depenses, id=depense_id)
    if request.method == 'POST':
        try:
            depense.montant = int(request.POST.get('montant'))
            depense.statut_validation = request.POST.get('statut_validation')
            depense.save()
            messages.success(request, "Dépense mise à jour avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard_tresorerie'))

def modifier_depense(request, pk):
    depense = get_object_or_404(Depenses, pk=pk)
    if request.method == 'POST':
        form = DepenseForm(request.POST, request.FILES, instance=depense)
        if form.is_valid():
            form.save()
            return redirect('liste_depenses')
    else:
        form = DepenseForm(instance=depense)
    return render(request, 'frontoffice/depenses/form_depense.html', {'form': form, 'action': 'Modifier'})

def supprimer_depense(request, pk):
    depense = get_object_or_404(Depenses, pk=pk)
    if request.method == 'POST':
        depense.delete()
        return redirect('liste_depenses')
    return render(request, 'frontoffice/depenses/confirm_delete.html', {'objet': depense})



# === CAISSE PRINCIPALE ============================================================================================================================
from django.http import JsonResponse
from django.utils import timezone

@fonctionnalite_autorisee('enregistrer_dotation') 
def enregistrer_dotation(request, caisse_id):
    annee_active = AnneeScolaires.objects.filter(active=True).first()

    try:
        caisse = Caisses.objects.get(pk=caisse_id)
        caissep = CaisseCentrales.objects.all().first()
        montant = int(request.POST.get('montant'))

        if montant <= 0:
            return JsonResponse({'success': False, 'error': "Le montant doit être supérieur à zéro."})

        if not caissep:
            return JsonResponse({'success': False, 'error': "Caisse centrale introuvable."})

        # Créer l'opération de type 'entrée'
        operation = Operations.objects.create(
            caisse=caissep,
            type_operation='entree',
            montant=montant,
            date_operation=timezone.now().date(),
            responsable=request.user,
            motif = f"Dotation de fonctionnement pour {caisse.etablissement.nom}",
            commentaire = f"Dotation de fonctionnement pour {caisse.etablissement.nom}",
            annee_scolaire=annee_active,
            etablissement=caisse.etablissement
        )

        # Mettre à jour le solde initial de la caisse d’établissement
        caisse.solde_initial += montant
        caisse.save()

        return JsonResponse({'success': True})
    
    except Caisses.DoesNotExist:
        return JsonResponse({'success': False, 'error': "Caisse de l'établissement introuvable."})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

    

@fonctionnalite_autorisee('detail_caisse_principale') 
def detail_caisse_principale(request):
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    
    # Filtrer une seule caisse de l'établissement et de l'année scolaire active
    caisses = CaisseCentrales.objects.get()

    operations = Operations.objects.filter(caisse=caisses).order_by('-date_operation') if caisses else []
 
    
    context = {
        'annee_active': annee_active,
        'caisses': caisses,
        'operations': operations,
    }
    return render(request, 'backoffice/caisses/detail_caisse_principale.html', context)


def liste_operationsOK(request, caisse_id):
    caisse = get_object_or_404(CaisseCentrales, id=caisse_id)
    operations = caisse.operations.order_by('-date_operation')
    return render(request, 'backoffice/caisses/operations/liste.html', {
        'operations': operations,
        'caisse': caisse,
    })

@fonctionnalite_autorisee('liste_operations') 
def liste_operations(request, caisse_id):
    caisse = get_object_or_404(CaisseCentrales, id=caisse_id)
    operations = caisse.operations.order_by('-date_operation')

    total_entrees = operations.filter(type_operation='entree').aggregate(total=Sum('montant'))['total'] or 0
    total_sorties = operations.filter(type_operation='sortie').aggregate(total=Sum('montant'))['total'] or 0
    solde = total_entrees - total_sorties

    return render(request, 'backoffice/caisses/operations/liste.html', {
        'caisse': caisse,
        'operations': operations,
        'total_entrees': total_entrees,
        'total_sorties': total_sorties,
        'solde': solde,
    })

from django.utils.timezone import now
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.db.models import Sum
from django.utils.timezone import now
from .models import CaisseCentrales, Operations, AnneeScolaires

def liste_operations_pointsOK(request, caisse_id):
    caisse = get_object_or_404(CaisseCentrales, id=caisse_id)
    annee_active = AnneeScolaires.objects.filter(active=True).first()

    operations = Operations.objects.filter(caisse=caisse, annee_scolaire=annee_active).order_by('-date_operation')

    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')

    if date_debut and date_fin:
        operations = operations.filter(date_operation__range=[date_debut, date_fin])
    else:
        today = now().date()
        date_debut = date_fin = today.isoformat()
        operations = operations.filter(date_operation=today)

    total_entree = operations.filter(type_operation='entree').aggregate(Sum('montant'))['montant__sum'] or 0
    total_sortie = operations.filter(type_operation='sortie').aggregate(Sum('montant'))['montant__sum'] or 0
    solde = total_entree - total_sortie
    
    context = {
        'caisse': caisse,
        'operations': operations,
        'total_entree': total_entree,
        'total_sortie': total_sortie,
        'solde': solde,
        'date_debut': date_debut,
        'date_fin': date_fin,
    }
    return render(request, 'backoffice/caisses/operations/liste_operations_points.html', context)

@fonctionnalite_autorisee('liste_operations_points') 
def liste_operations_points(request, caisse_id):
    caisse = get_object_or_404(CaisseCentrales, id=caisse_id)
    #operations = caisse.operations.select_related('responsable').order_by('-date_operation')
    annee_active = AnneeScolaires.objects.filter(active=True).first()
    operations = Operations.objects.filter(caisse=caisse,annee_scolaire=annee_active).order_by('-date_operation') if caisse else []

    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')

    if date_debut and date_fin:
        operations = operations.filter(date_operation__range=[date_debut, date_fin])
    else:
        today = now().date()
        operations = operations.filter(date_operation=today)

    total_entree = operations.filter(type_operation='entree').aggregate(Sum('montant'))['montant__sum'] or 0
    total_sortie = operations.filter(type_operation='sortie').aggregate(Sum('montant'))['montant__sum'] or 0
    solde = total_entree - total_sortie
    
    context = {
        'caisse': caisse,
        'operations': operations,
        'total_entree': total_entree,
        'total_sortie': total_sortie,
        'solde' : solde
    }
    return render(request, 'backoffice/caisses/operations/liste_operations_points.html', context)


import openpyxl
from django.http import HttpResponse
from django.utils.timezone import now

def export_operations_excel(request, caisse_id):
    caisse = get_object_or_404(CaisseCentrales, id=caisse_id)
    operations = caisse.operations.order_by('-date_operation')

    # Filtrage par intervalle de dates (optionnel)
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    if date_debut and date_fin:
        operations = operations.filter(date_operation__range=[date_debut, date_fin])
    else:
        today = now().date()
        operations = operations.filter(date_operation=today)

    # Création du classeur Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Opérations {caisse.nom}"

    # En-têtes
    headers = ['Date', 'Type', 'Motif', 'Montant (FCFA)', 'Responsable']
    ws.append(headers)

    # Données
    for op in operations:
        ws.append([
            op.date_operation.strftime('%Y-%m-%d'),
            op.get_type_operation_display(),
            op.motif or '-',
            op.montant,
            str(op.responsable) if op.responsable else '-',
        ])

    # Réponse HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    filename = f"operations_caisse_{caisse.nom}_{date_debut or 'aujourdhui'}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response

from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from django.utils.timezone import now

def export_operations_pdf(request, caisse_id):
    caisse = get_object_or_404(CaisseCentrales, id=caisse_id)
    operations = caisse.operations.order_by('-date_operation')

    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    if date_debut and date_fin:
        operations = operations.filter(date_operation__range=[date_debut, date_fin])
    else:
        today = now().date()
        operations = operations.filter(date_operation=today)

    html_string = render_to_string('backoffice/caisses/operations/operations_pdf.html', {
        'caisse': caisse,
        'operations': operations,
        'date_debut': date_debut,
        'date_fin': date_fin,
    })

    html = HTML(string=html_string)
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"operations_caisse_{caisse.nom}_{date_debut or 'aujourdhui'}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


def ajouter_operationE(request, caisse_id):
    caisse = get_object_or_404(CaisseCentrales, id=caisse_id) if caisse_id != 0 else None
    annee_active = AnneeScolaires.objects.filter(active=True).first()

    if request.method == 'POST':
        form = OperationForm(request.POST, request.FILES)
        if form.is_valid():
            operation = form.save(commit=False)
            operation.annee_scolaire = annee_active
            operation.responsable = request.user
            if caisse:
                operation.caisse = caisse
            
            operation.save()
                
            return redirect('liste_operations', caisse_id=caisse.id)
            

    else:
        form = OperationForm()

    return render(request, 'backoffice/caisses/operations/ajouter.html', {
        'form': form,
        'caisse': caisse
    })

@fonctionnalite_autorisee('ajouter_operation') 
def ajouter_operation(request, caisse_id):
    caisse = get_object_or_404(CaisseCentrales, id=caisse_id) if caisse_id != 0 else None
    annee_active = AnneeScolaires.objects.filter(active=True).first()

    if request.method == 'POST':
        # Créer une instance temporaire avec caisse assignée
        operation_temp = Operations(caisse=caisse)

        # Passer cette instance à OperationForm (via instance=)
        form = OperationForm(request.POST, request.FILES, instance=operation_temp)

        if form.is_valid():
            operation = form.save(commit=False)
            operation.annee_scolaire = annee_active
            operation.responsable = request.user

            # Ici operation.caisse est déjà défini car form a l'instance avec caisse
            operation.save()
            return redirect('liste_operations', caisse_id=caisse.id)
    else:
        form = OperationForm()

    return render(request, 'backoffice/caisses/operations/ajouter.html', {
        'form': form,
        'caisse': caisse
    })

@fonctionnalite_autorisee('modifier_operation') 
def modifier_operationB(request, id):
    operation = get_object_or_404(Operations, id=id)
    if request.method == 'POST':
        form = OperationForm(request.POST, request.FILES, instance=operation)
        if form.is_valid():
            form.save()
            messages.success(request, "Opération modifiée.")
            return redirect('liste_operations', caisse_id=operation.caisse.id)
    else:
        form = OperationForm(instance=operation)

    return render(request, 'backoffice/caisses/operations/modifier.html', {
        'form': form,
        'operation': operation,
    })


from django.contrib import messages


def modifier_operation(request, id):
    operation = get_object_or_404(Operations, id=id)
    ancien_montant = operation.montant

    if request.method == 'POST':
        form = OperationForm(request.POST, request.FILES, instance=operation)
        if form.is_valid():
            nouvelle_operation = form.save(commit=False)
            nouveau_montant = nouvelle_operation.montant

            # Si l'opération concerne une caisse d'établissement
            if hasattr(operation, 'etablissement') and operation.etablissement is not None:
                caisse = Caisses.objects.filter(
                    annee_scolaire=operation.annee_scolaire,
                    etablissement=operation.etablissement
                ).first()

                if caisse:
                    difference = nouveau_montant - ancien_montant
                    caisse.solde_initial += difference
                    caisse.save()

            nouvelle_operation.save()
             #messages.success(request, "Opération modifiée.")
            return redirect('liste_operations', caisse_id=operation.caisse.id)
    else:
        form = OperationForm(instance=operation)

    return render(request, 'backoffice/caisses/operations/modifier.html', {
        'form': form,
        'operation': operation,
    })


@fonctionnalite_autorisee('supprimer_operation') 
def supprimer_operation(request, id):
    operation = get_object_or_404(Operations, id=id)
    caisse_id = operation.caisse.id
    operation.delete()
    messages.success(request, "Opération supprimée.")
    return redirect('liste_operations', caisse_id=caisse_id)
