from .serializers import AerodromeSerializer
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from ..constants import NOT_ADMITTED_STATE, PENDING_ADMISSION_STATE, PENDING_VERIFICATION_STATE, PUBLISHED_STATE
from ..models import Aerodrome, Agent, DemandeAIC, DemandeNOTAM, DemandeSUPP, LocalAgent, LocalInformer, LocalInformerAction, SourceStructureAction, Unit
from .permissions import CanInitiateDDIA, IsAuthorityLocalInformer, IsNationalInformer, IsSourceCommander, IsVerifier
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from datetime import datetime

notam_type = ContentType.objects.get_for_model(DemandeNOTAM)
suppaip_type = ContentType.objects.get_for_model(DemandeSUPP)
aic_type = ContentType.objects.get_for_model(DemandeAIC)

def get_ddia_count_unit(unit: Unit, all_ddia: str, year: str):
    try:
        year = int(year)
    except:
        year = datetime.now().year
    if all_ddia == 'yes':
        countAIC = DemandeAIC.objects.filter(unit=unit, deposit_datetime__year=year).count()
        countSUPP = DemandeSUPP.objects.filter(unit=unit, deposit_datetime__year=year).count()
        countNOTAM = DemandeNOTAM.objects.filter(unit=unit, deposit_datetime__year=year).count()
    else:
        countAIC = DemandeAIC.objects.filter(unit=unit, deposit_datetime__year=year, state=PUBLISHED_STATE).count()
        countSUPP = DemandeSUPP.objects.filter(unit=unit, deposit_datetime__year=year, state=PUBLISHED_STATE).count()
        countNOTAM = DemandeNOTAM.objects.filter(unit=unit, deposit_datetime__year=year, state=PUBLISHED_STATE).count()     
    data = {
        'countAIC': countAIC,
        'countSUPP': countSUPP,
        'countNOTAM': countNOTAM
    }    
    return data

def get_ddia_admitted_count_unit(unit: Unit, all_ddia: str, year: str):
    try:
        year = int(year)
    except:
        year = datetime.now().year
    if all_ddia == 'yes':
        countNOTAM = SourceStructureAction.objects.filter(agent__aerodrome=unit.aerodrome, date_time__year=year,
            prev_state=PENDING_ADMISSION_STATE, notam__unit=unit).exclude(new_state=NOT_ADMITTED_STATE).count()
        countAIC = SourceStructureAction.objects.filter(agent__aerodrome=unit.aerodrome, date_time__year=year,
            prev_state=PENDING_ADMISSION_STATE, aic__unit=unit).exclude(new_state=NOT_ADMITTED_STATE).count()
        countSUPP = SourceStructureAction.objects.filter(agent__aerodrome=unit.aerodrome, date_time__year=year,
            prev_state=PENDING_ADMISSION_STATE, suppaip__unit=unit).exclude(new_state=NOT_ADMITTED_STATE).count()
    else:
        countNOTAM = SourceStructureAction.objects.filter(agent__aerodrome=unit.aerodrome, date_time__year=year,
            prev_state=PENDING_ADMISSION_STATE, notam__state=PUBLISHED_STATE, notam__unit=unit).exclude(new_state=NOT_ADMITTED_STATE).count()
        countAIC = SourceStructureAction.objects.filter(agent__aerodrome=unit.aerodrome, date_time__year=year,
            prev_state=PENDING_ADMISSION_STATE, aic__state=PUBLISHED_STATE, aic__unit=unit).exclude(new_state=NOT_ADMITTED_STATE).count()
        countSUPP = SourceStructureAction.objects.filter(agent__aerodrome=unit.aerodrome, date_time__year=year,
            prev_state=PENDING_ADMISSION_STATE, suppaip__state=PUBLISHED_STATE, suppaip__unit=unit).exclude(new_state=NOT_ADMITTED_STATE).count()
    data = {
        'countAIC': countAIC,
        'countSUPP': countSUPP,
        'countNOTAM': countNOTAM
    }    
    return data

def get_ddia_count_aerodrome(aerodrome: Aerodrome, all_ddia: str, year: str):
    try:
        year = int(year)
    except:
        year = datetime.now().year
    if all_ddia == 'yes':
        countNOTAM = SourceStructureAction.objects.filter(agent__aerodrome=aerodrome, date_time__year=year,
            prev_state=PENDING_ADMISSION_STATE, ddia_type=notam_type).exclude(new_state=NOT_ADMITTED_STATE).count()
        countAIC = SourceStructureAction.objects.filter(agent__aerodrome=aerodrome, date_time__year=year,
            prev_state=PENDING_ADMISSION_STATE, ddia_type=aic_type).exclude(new_state=NOT_ADMITTED_STATE).count()
        countSUPP = SourceStructureAction.objects.filter(agent__aerodrome=aerodrome, date_time__year=year,
            prev_state=PENDING_ADMISSION_STATE, ddia_type=suppaip_type).exclude(new_state=NOT_ADMITTED_STATE).count()
    else:
        countNOTAM = SourceStructureAction.objects.filter(agent__aerodrome=aerodrome, date_time__year=year,
            prev_state=PENDING_ADMISSION_STATE, notam__state=PUBLISHED_STATE).exclude(new_state=NOT_ADMITTED_STATE).count()
        countAIC = SourceStructureAction.objects.filter(agent__aerodrome=aerodrome, date_time__year=year,
            prev_state=PENDING_ADMISSION_STATE, aic__state=PUBLISHED_STATE).exclude(new_state=NOT_ADMITTED_STATE).count()
        countSUPP = SourceStructureAction.objects.filter(agent__aerodrome=aerodrome, date_time__year=year,
            prev_state=PENDING_ADMISSION_STATE, suppaip__state=PUBLISHED_STATE).exclude(new_state=NOT_ADMITTED_STATE).count()
    data = {
        'countAIC': countAIC,
        'countSUPP': countSUPP,
        'countNOTAM': countNOTAM
    }    
    return data

@api_view(['GET'])
@permission_classes([IsAuthenticated, CanInitiateDDIA])
def get_stats_datas_for_source(request):
    allDDIA = request.GET.get('all')
    year = request.GET.get('year')
    agent = Agent.objects.filter(user = request.user).first()
    if agent:
        unit = agent.unit
    else:
        agent = LocalAgent.objects.get(user = request.user)
        unit = agent.localinformer.unit
    ddia_count = get_ddia_count_unit(unit, all_ddia=allDDIA, year=year)
    data = {
        'unit': unit.name,
        'ddia_count': ddia_count
    }
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsVerifier])
def get_stats_datas_for_sourceverifier(request):
    agent = Agent.objects.filter(user = request.user).first()
    if agent:
        aerodrome = agent.aerodrome
    else:
        agent = LocalAgent.objects.get(user=request.user)
        aerodrome = agent.localinformer.aerodrome
    allDDIA = request.GET.get('all')
    year = request.GET.get('year')
    ddia_count_by_unit = request.GET.get('count_by_unit')   
    units = Unit.objects.filter(aerodrome=aerodrome)
    if ddia_count_by_unit == 'yes':
        data = []
        for unit in units:
            data.append({
                'unit': unit.name,
                'ddia_count': get_ddia_admitted_count_unit(unit, allDDIA, year)
            })
        return Response(data, status=status.HTTP_200_OK)
    else:
        data = {
            'aerodrome': AerodromeSerializer(aerodrome).data,
            'ddia_count': get_ddia_count_aerodrome(aerodrome, allDDIA, year)
        }
        return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSourceCommander])
def get_stats_datas_for_sourcestructure(request):
    allDDIA = request.GET.get('all')
    year = request.GET.get('year')
    ddia_count_by_unit = request.GET.get('count_by_unit')
    agent = Agent.objects.get(user = request.user)
    aerodrome = agent.aerodrome
    units = Unit.objects.filter(aerodrome=aerodrome)
    if ddia_count_by_unit == 'yes':
        data = []
        for unit in units:
            data.append({
                'unit': unit.name,
                'ddia_count': get_ddia_admitted_count_unit(unit, allDDIA, year)
            })
        return Response(data, status=status.HTTP_200_OK)
    else:
        data = {
            'aerodrome': AerodromeSerializer(aerodrome).data,
            'ddia_count': get_ddia_count_aerodrome(aerodrome, allDDIA, year)
        }
        return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAuthorityLocalInformer])
def get_stats_datas_for_localinformer(request):
    aerodromes = Aerodrome.objects.all()
    allDDIA = request.GET.get('all')
    year = request.GET.get('year')
    data = []
    for aerodrome in aerodromes:    
        data.append({
            'aerodrome': AerodromeSerializer(aerodrome).data,
            'ddia_count': get_ddia_count_aerodrome(aerodrome, allDDIA, year)
        })
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsNationalInformer])
def get_stats_datas_for_nationalinformer(request):
    aerodromes = Aerodrome.objects.all()
    print(aerodromes)
    allDDIA = request.GET.get('all')
    year = request.GET.get('year')
    data = []
    for aerodrome in aerodromes:    
        data.append({
            'aerodrome': AerodromeSerializer(aerodrome).data,
            'ddia_count': get_ddia_count_aerodrome(aerodrome, allDDIA, year)
        })
    print(data)
    return Response(data, status=status.HTTP_200_OK)