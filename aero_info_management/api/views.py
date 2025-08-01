import re
from .permissions import *
from rest_framework import generics, mixins , response, status, views, viewsets, filters
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from .serializers import *
from .ddia_serializers import *
from .agents_serializers import *
from ..constants import *
from django.db.models import Q
from rest_framework import permissions
from django.db import transaction
from ..models import *


notam_type = ContentType.objects.get_for_model(DemandeNOTAM)
suppaip_type = ContentType.objects.get_for_model(DemandeSUPP)
aic_type = ContentType.objects.get_for_model(DemandeAIC)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsNationalInformer])
def listDDIA_inwaiting_for_nationalinf_view(request, type_ddia):
    national_agent = NationalAgent.objects.select_related('nationalinformer').get(user=request.user)
    nationalinf = national_agent.nationalinformer
    validations = []
    if type_ddia == 'notam':
        validations = LocalInformerAction.objects.filter(
            notam__state=PENDING_APPROVAL_STATE, target_nationalinf=nationalinf)
    elif type_ddia == 'suppaip':
        validations = LocalInformerAction.objects.filter(
            suppaip__state=PENDING_APPROVAL_STATE, target_nationalinf=nationalinf)
    elif type_ddia == 'aic':
        validations = LocalInformerAction.objects.filter(
            aic__state=PENDING_APPROVAL_STATE, target_nationalinf=nationalinf)
    else:
        validations = LocalInformerAction.objects.filter(
            Q(aic_state=PENDING_APPROVAL_STATE) |Q(notam_state=PENDING_APPROVAL_STATE) | Q(suppaip_state=PENDING_APPROVAL_STATE),
            target_nationalinf=nationalinf
        )
    data = LocalInformerActionSerializer(validations, many=True, context={'request': request}).data
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAuthorityLocalInformer])
def listDDIA_inwaiting_for_authoritylocalinformer_view(request, type_ddia):
    actionsagent = []
    if type_ddia == 'notam':
        actionsagent = SourceStructureAction.objects.filter(notam__state=PENDING_VALIDATION_STATE)
    elif type_ddia == 'suppaip':
        actionsagent = SourceStructureAction.objects.filter(suppaip__state=PENDING_VALIDATION_STATE)
    elif type_ddia == 'aic':
        actionsagent = SourceStructureAction.objects.filter(aic__state=PENDING_VALIDATION_STATE)
    else:
        actionsagent = SourceStructureAction.objects.filter(Q(notam__state=PENDING_VALIDATION_STATE) 
         | Q(aic__state=PENDING_VALIDATION_STATE) | Q(suppaip__state=PENDING_VALIDATION_STATE))       
    data = SourceStructureActionSerializer(actionsagent, many=True, context={'request': request}).data
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSourceCommander])
def listDDIA_inwaiting_for_sourcestructure_view(request, type_ddia):
    has_localinf = request.GET.get('from_localinf') == 'yes'
    if has_localinf:
        agent = LocalAgent.objects.select_related('aerodrome').get(user = request.user)
        aerodrome = agent.aerodrome
        actionsagent = []
        if type_ddia == 'notam':
            actionsagent = LocalInformerAction.objects.filter(
                notam__unit__aerodrome=aerodrome, notam__state=PENDING_ADMISSION_STATE)
        elif type_ddia == 'suppaip':
            actionsagent = LocalInformerAction.objects.filter(
                suppaip__unit__aerodrome=aerodrome, suppaip__state=PENDING_ADMISSION_STATE)
        elif type_ddia == 'aic':
            actionsagent = LocalInformerAction.objects.filter(
                aic__unit__aerodrome=aerodrome, aic__state=PENDING_ADMISSION_STATE)
        else:
            actionsagent = LocalInformerAction.objects.filter(
            Q(notam__unit__aerodrome=aerodrome, notam__state=PENDING_ADMISSION_STATE) 
            | Q(aic__unit__aerodrome=aerodrome, aic__state=PENDING_ADMISSION_STATE) 
            | Q(suppaip__unit__aerodrome=aerodrome, suppaip__state=PENDING_ADMISSION_STATE), 
            )
        data = SourceStructureActionSerializer(actionsagent, many=True, context={'request': request}).data    
    else:
        agent = Agent.objects.select_related('aerodrome').get(user = request.user)
        aerodrome = agent.aerodrome
        actionsagent = []
        if type_ddia == 'notam':
            actionsagent = SourceStructureAction.objects.filter(
                notam__unit__aerodrome=aerodrome, notam__state=PENDING_ADMISSION_STATE)
        elif type_ddia == 'suppaip':
            actionsagent = SourceStructureAction.objects.filter(
                suppaip__unit__aerodrome=aerodrome, suppaip__state=PENDING_ADMISSION_STATE)
        elif type_ddia == 'aic':
            actionsagent = SourceStructureAction.objects.filter(
                aic__unit__aerodrome=aerodrome, aic__state=PENDING_ADMISSION_STATE)
        else:
            actionsagent = SourceStructureAction.objects.filter(
            Q(notam__unit__aerodrome=aerodrome, notam__state=PENDING_ADMISSION_STATE) 
            | Q(aic__unit__aerodrome=aerodrome, aic__state=PENDING_ADMISSION_STATE) 
            | Q(suppaip__unit__aerodrome=aerodrome, suppaip__state=PENDING_ADMISSION_STATE), 
            )
        data = SourceStructureActionSerializer(actionsagent, many=True, context={'request': request}).data
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsVerifier])
def listDDIA_inwaiting_for_sourceverifier_view(request, type_ddia):
    islocalinf = request.GET.get('is_localinf') == 'yes'
    user = request.user
    if islocalinf:
        aerodrome = LocalAgent.objects.get(user=user).localinformer.aerodrome
    else:
        aerodrome = Agent.objects.get(user=user).aerodrome
    actionsagent = []
    if type_ddia == 'notam':
        actionsagent = SourceStructureAction.objects.filter(
            notam__unit__aerodrome=aerodrome,  notam__state=PENDING_VERIFICATION_STATE)
    elif type_ddia == 'suppaip':
        actionsagent = SourceStructureAction.objects.filter(
            suppaip__unit__aerodrome=aerodrome,  suppaip__state=PENDING_VERIFICATION_STATE)
    elif type_ddia == 'aic':
        actionsagent = SourceStructureAction.objects.filter(
            aic__unit__aerodrome=aerodrome,  aic__state=PENDING_VERIFICATION_STATE)
    else:
        actionsagent = SourceStructureAction.objects.filter(
           Q(notam__unit__aerodrome=aerodrome,  notam__state=PENDING_VERIFICATION_STATE) 
         | Q(aic__unit__aerodrome=aerodrome,  aic__state=PENDING_VERIFICATION_STATE) 
         | Q(suppaip__unit__aerodrome=aerodrome,  suppaip__state=PENDING_VERIFICATION_STATE), 
        )
    data = SourceStructureActionSerializer(actionsagent, many=True, context={'request': request}).data
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
def listDDIA_inwaiting_for_initiator_view(request):
    return response.Response({})

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsNationalInformer])
def listDDIA_processed_for_nationalinf_view(request, type_ddia):
    national_agent = NationalAgent.objects.select_related('nationalinformer').get(user=request.user)
    nationalinf = national_agent.nationalinformer
    approbations = []
    if type_ddia == 'notam':
        approbations = NationalInformerAction.objects.filter(ddia_type=notam_type)
    elif type_ddia == 'suppaip':
        approbations = NationalInformerAction.objects.filter(ddia_type=suppaip_type)
    elif type_ddia == 'aic':
        approbations = NationalInformerAction.objects.filter(ddia_type=aic_type)
    else:
        approbations = NationalInformerAction.objects.all()
        if not nationalinf.is_authority:
            approbations = approbations.filter(national_agent__nationalinformer=nationalinf)
    data = NationalInformerActionSerializer(approbations, many=True, context={'request': request}).data
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAuthorityLocalInformer])
def listDDIA_processed_for_authoritylocalinformer_view(request, type_ddia):
    local_agent = LocalAgent.objects.select_related('localinformer').get(user=request.user)
    localinf = local_agent.localinformer
    validations = []
    if type_ddia == 'notam':
        validations = LocalInformerAction.objects.filter(
            local_agent__localinformer=localinf, ddia_type=notam_type)
    elif type_ddia == 'suppaip':
        validations = LocalInformerAction.objects.filter(
            local_agent__localinformer=localinf, ddia_type=suppaip_type)
    elif type_ddia == 'aic':
        validations = LocalInformerAction.filter(
            local_agent__localinformer=localinf, ddia_type=aic_type)
    else:
        validations = LocalInformerAction.objects.filter(
            local_agent__localinformer=localinf,  prev_state=PENDING_VALIDATION_STATE
        )
    data = LocalInformerActionSerializer(validations, many=True, context={'request': request}).data
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSourceCommander])
def listDDIA_processed_for_sourcestructure_view(request, type_ddia):
    agent = Agent.objects.select_related('aerodrome').get(user = request.user)
    aerodrome = agent.aerodrome
    actionsagent = []
    if type_ddia == 'notam':
        actionsagent = SourceStructureAction.objects.filter(
            notam__unit__aerodrome=aerodrome,  prev_state=PENDING_ADMISSION_STATE)
    elif type_ddia == 'suppaip':
        actionsagent = SourceStructureAction.objects.filter(
            suppaip__unit__aerodrome=aerodrome,  prev_state=PENDING_ADMISSION_STATE)
    elif type_ddia == 'aic':
        actionsagent = SourceStructureAction.objects.filter(
            aic__unit__aerodrome=aerodrome,  prev_state=PENDING_ADMISSION_STATE)
    else:
        actionsagent = SourceStructureAction.objects.filter(
            Q(notam__unit__aerodrome=aerodrome) |  Q(aic__unit__aerodrome=aerodrome) | Q(suppaip__unit__aerodrome=aerodrome), 
            prev_state=PENDING_ADMISSION_STATE
        )
    data = SourceStructureActionSerializer(actionsagent, many=True, context={'request': request}).data
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsVerifier])
def listDDIA_processed_for_sourceverifier_view(request, type_ddia):
    islocalinf = request.GET.get('is_localinf') == 'yes'
    user = request.user
    if islocalinf:
        localagent = LocalAgent.objects.select_related('localinformer__aerodrome').get(user = user)
        aerodrome = localagent.localinformer.aerodrome
        actionsagent = []
        if type_ddia == 'notam':
            actionsagent = LocalInformerAction.objects.filter(notam__unit__aerodrome=aerodrome,  prev_state=PENDING_VERIFICATION_STATE)
        elif type_ddia == 'suppaip':
            actionsagent = LocalInformerAction.objects.filter(suppaip__unit__aerodrome=aerodrome,  prev_state=PENDING_VERIFICATION_STATE)
        elif type_ddia == 'aic':
            actionsagent = LocalInformerAction.objects.filter(aic__unit__aerodrome=aerodrome,  prev_state=PENDING_VERIFICATION_STATE)
        else:
            actionsagent = LocalInformerAction.objects.filter(
                Q(notam__unit__aerodrome=aerodrome) |  Q(aic__unit__aerodrome=aerodrome) | Q(suppaip__unit__aerodrome=aerodrome), 
                prev_state=PENDING_VERIFICATION_STATE
            )
        data = SourceStructureActionSerializer(actionsagent, many=True, context={'request': request}).data   
    else:
        agent = Agent.objects.select_related('aerodrome').get(user = user)
        aerodrome = agent.aerodrome
        actionsagent = []
        if type_ddia == 'notam':
            actionsagent = SourceStructureAction.objects.filter(notam__unit__aerodrome=aerodrome,  prev_state=PENDING_VERIFICATION_STATE)
        elif type_ddia == 'suppaip':
            actionsagent = SourceStructureAction.objects.filter(suppaip__unit__aerodrome=aerodrome,  prev_state=PENDING_VERIFICATION_STATE)
        elif type_ddia == 'aic':
            actionsagent = SourceStructureAction.objects.filter(aic__unit__aerodrome=aerodrome,  prev_state=PENDING_VERIFICATION_STATE)
        else:
            actionsagent = SourceStructureAction.objects.filter(
                Q(notam__unit__aerodrome=aerodrome) |  Q(aic__unit__aerodrome=aerodrome) | Q(suppaip__unit__aerodrome=aerodrome), 
                prev_state=PENDING_ADMISSION_STATE
            )
        data = SourceStructureActionSerializer(actionsagent, many=True, context={'request': request}).data    
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, CanInitiateDDIA])
def listDDIA_processed_for_initiator_view(request, type_ddia):
    agent = Agent.objects.select_related('unit').get(user = request.user)
    ownunit = agent.unit
    data = []
    if type_ddia == 'notam':
        demandes_notam = DemandeNOTAM.objects.filter(unit=ownunit)
        data = DemandeNOTAMSerializer(demandes_notam, many=True, context={'request': request}).data
    elif type_ddia == 'suppaip':
        demandes_suppaip = DemandeSUPP.objects.filter(unit=ownunit) 
        data = DemandeSUPPSerializer(demandes_suppaip, many=True, context={'request': request}).data
    elif type_ddia == 'aic':
        demandes_aic = DemandeAIC.objects.filter(unit=ownunit)  
        data = DemandeAICSerializer(demandes_aic, many=True, context={'request': request}).data
    return response.Response(data=data, status=status.HTTP_200_OK)


class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    http_method_names = ['get', 'post', 'head']

class LocalAgentViewSet(viewsets.ModelViewSet):
    queryset = LocalAgent.objects.all()
    serializer_class = LocalAgentSerializer
    http_method_names = ['get', 'post', 'head']

class NationalAgentViewSet(viewsets.ModelViewSet):
    queryset = NationalAgent.objects.all()
    serializer_class = NationalAgentSerializer
    http_method_names = ['get', 'post', 'head']

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UnitSerializer
    http_method_names = ['get', 'post', 'put', 'head', 'patch']

class AerodromeViewSet(viewsets.ModelViewSet):
    queryset = Aerodrome.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AerodromeSerializer
    http_method_names = ['get', 'post', 'put', 'head', 'patch']

class LocalInformerViewSet(viewsets.ModelViewSet):
    queryset = LocalInformer.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = LocalInformerSerializer 
    http_method_names = ['get', 'post', 'put', 'head', 'patch']

class NationalInformerViewSet(viewsets.ModelViewSet):
    queryset = NationalInformer.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = NationalInformerSerializer
    http_method_names = ['get', 'post', 'put', 'head', 'patch']

