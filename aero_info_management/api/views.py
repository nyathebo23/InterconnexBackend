from .permissions import CanInitiateDDIA, IsLocalInformer, IsNationalInformer, IsOwner, IsSourceCommander, IsVerifier
from rest_framework import generics, mixins , response, status, views, viewsets, filters
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from .serializers import *
from ..constants import *
from django.db.models import Q
from rest_framework import permissions
from django.db import transaction

notam_type = ContentType.objects.get_for_model(DemandeNOTAM)
suppaip_type = ContentType.objects.get_for_model(DemandeSUPP)
aic_type = ContentType.objects.get_for_model(DemandeAIC)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsNationalInformer])
def listDDIA_inwaiting_for_nationalinformer_view(request, type_ddia):
    national_agent = NationalAgent.objects.select_related('nationalinformer').get(user=request.user)
    nationalinf = national_agent.nationalinformer
    validations = []
    if type_ddia == 'notam':
        validations = Validation.objects.filter(
            # local_agent__localinformer__national_informer=nationalinf, 
            notam__state=PENDING_APPROVAL_STATE)
    elif type_ddia == 'suppaip':
        validations = Validation.objects.filter(
            # local_agent__localinformer__national_informer=nationalinf, 
            suppaip__state=PENDING_APPROVAL_STATE)
    elif type_ddia == 'aic':
        validations = Validation.objects.filter(
            # local_agent__localinformer__national_informer=nationalinf, 
            aic__state=PENDING_APPROVAL_STATE)
    else:
        validations = Validation.objects.filter(
            Q(aic_state=PENDING_APPROVAL_STATE) |Q(notam_state=PENDING_APPROVAL_STATE) | Q(suppaip_state=PENDING_APPROVAL_STATE)
        )
    data = ValidationSerializer(validations, many=True, context={'request': request}).data
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsLocalInformer])
def listDDIA_inwaiting_for_localinformer_view(request, type_ddia):
    local_agent = LocalAgent.objects.select_related('localinformer').get(user=request.user)
    localinf = local_agent.localinformer
    actionsagent = []
    if type_ddia == 'notam':
        actionsagent = ActionAgentOnDDIA.objects.filter(
            notam__unit__aerodrome__local_informer=localinf, notam__state=PENDING_VALIDATION_STATE)
    elif type_ddia == 'suppaip':
        actionsagent = ActionAgentOnDDIA.objects.filter(
            suppaip__unit__aerodrome__local_informer=localinf, suppaip__state=PENDING_VALIDATION_STATE)
    elif type_ddia == 'aic':
        actionsagent = ActionAgentOnDDIA.objects.filter(
            aic__unit__aerodrome__local_informer=localinf, aic__state=PENDING_VALIDATION_STATE)
    else:
        actionsagent = ActionAgentOnDDIA.objects.filter(
           Q(notam__unit__aerodrome__local_informer=localinf, notam__state=PENDING_VALIDATION_STATE) 
         | Q(aic__unit__aerodrome__local_informer=localinf, aic__state=PENDING_VALIDATION_STATE) 
         | Q(suppaip__unit__aerodrome__local_informer=localinf, suppaip__state=PENDING_VALIDATION_STATE), 
        )       
    data = ActionAgentOnDDIASerializer(actionsagent, many=True, context={'request': request}).data
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSourceCommander])
def listDDIA_inwaiting_for_sourcestructure_view(request, type_ddia):
    agent = Agent.objects.select_related('source_structure').get(user = request.user)
    sourcestructure = agent.source_structure
    actionsagent = []
    if type_ddia == 'notam':
        actionsagent = ActionAgentOnDDIA.objects.filter(
            notam__unit__aerodrome=sourcestructure, notam__state=PENDING_ADMISSION_STATE)
    elif type_ddia == 'suppaip':
        actionsagent = ActionAgentOnDDIA.objects.filter(
            suppaip__unit__aerodrome=sourcestructure, suppaip__state=PENDING_ADMISSION_STATE)
    elif type_ddia == 'aic':
        actionsagent = ActionAgentOnDDIA.objects.filter(
            aic__unit__aerodrome=sourcestructure, aic__state=PENDING_ADMISSION_STATE)
    else:
        actionsagent = ActionAgentOnDDIA.objects.filter(
           Q(notam__unit__aerodrome=sourcestructure, notam__state=PENDING_ADMISSION_STATE) 
         | Q(aic__unit__aerodrome=sourcestructure, aic__state=PENDING_ADMISSION_STATE) 
         | Q(suppaip__unit__aerodrome=sourcestructure, suppaip__state=PENDING_ADMISSION_STATE), 
        )
    data = ActionAgentOnDDIASerializer(actionsagent, many=True, context={'request': request}).data
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsVerifier])
def listDDIA_inwaiting_for_sourceverifier_view(request, type_ddia):
    agent = Agent.objects.select_related('source_structure').get(user = request.user)
    sourcestructure = agent.source_structure
    actionsagent = []
    if type_ddia == 'notam':
        actionsagent = ActionAgentOnDDIA.objects.filter(
            notam__unit__aerodrome=sourcestructure, notam__state=PENDING_VERIFICATION_STATE)
    elif type_ddia == 'suppaip':
        actionsagent = ActionAgentOnDDIA.objects.filter(
            suppaip__unit__aerodrome=sourcestructure, suppaip__state=PENDING_VERIFICATION_STATE)
    elif type_ddia == 'aic':
        actionsagent = ActionAgentOnDDIA.objects.filter(
            aic__unit__aerodrome=sourcestructure, aic__state=PENDING_VERIFICATION_STATE)
    else:
        actionsagent = ActionAgentOnDDIA.objects.filter(
           Q(notam__unit__aerodrome=sourcestructure, notam__state=PENDING_VERIFICATION_STATE) 
         | Q(aic__unit__aerodrome=sourcestructure, aic__state=PENDING_VERIFICATION_STATE) 
         | Q(suppaip__unit__aerodrome=sourcestructure, suppaip__state=PENDING_VERIFICATION_STATE), 
        )
    data = ActionAgentOnDDIASerializer(actionsagent, many=True, context={'request': request}).data

    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
def listDDIA_inwaiting_for_initiator_view(request):
    return response.Response({})

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsNationalInformer])
def listDDIA_processed_for_nationalinformer_view(request, type_ddia):
    national_agent = NationalAgent.objects.select_related('nationalinformer').get(user=request.user)
    nationalinf = national_agent.nationalinformer
    approbations = []
    if type_ddia == 'notam':
        approbations = Approbation.objects.filter(
            national_agent__nationalinformer=nationalinf, ddia_type=notam_type)
    elif type_ddia == 'suppaip':
        approbations = Approbation.objects.filter(
            national_agent__nationalinformer=nationalinf, ddia_type=suppaip_type)
    elif type_ddia == 'aic':
        approbations = Approbation.objects.filter(
            national_agent__nationalinformer=nationalinf, ddia_type=aic_type)
    else:
        approbations = Approbation.objects.filter(
            national_agent__nationalinformer=nationalinf
        )
    data = ApprobationSerializer(approbations, many=True, context={'request': request}).data

    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsLocalInformer])
def listDDIA_processed_for_localinformer_view(request, type_ddia):
    local_agent = LocalAgent.objects.select_related('localinformer').get(user=request.user)
    localinf = local_agent.localinformer
    validations = []
    if type_ddia == 'notam':
        validations = Validation.objects.filter(
            local_agent__localinformer=localinf, ddia_type=notam_type)
    elif type_ddia == 'suppaip':
        validations = Validation.objects.filter(
            local_agent__localinformer=localinf, ddia_type=suppaip_type)
    elif type_ddia == 'aic':
        validations = Validation.filter(
            local_agent__localinformer=localinf, ddia_type=aic_type)
    else:
        validations = Validation.objects.filter(
            local_agent__localinformer=localinf,  prev_state=PENDING_VALIDATION_STATE
        )
    data = ValidationSerializer(validations, many=True, context={'request': request}).data

    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSourceCommander])
def listDDIA_processed_for_sourcestructure_view(request, type_ddia):
    agent = Agent.objects.select_related('source_structure').get(user = request.user)
    sourcestructure = agent.source_structure
    actionsagent = []
    if type_ddia == 'notam':
        actionsagent = ActionAgentOnDDIA.objects.filter(
            notam__unit__aerodrome=sourcestructure, prev_state=PENDING_ADMISSION_STATE)
    elif type_ddia == 'suppaip':
        actionsagent = ActionAgentOnDDIA.objects.filter(
            suppaip__unit__aerodrome=sourcestructure, prev_state=PENDING_ADMISSION_STATE)
    elif type_ddia == 'aic':
        actionsagent = ActionAgentOnDDIA.objects.filter(
            aic__unit__aerodrome=sourcestructure, prev_state=PENDING_ADMISSION_STATE)
    else:
        actionsagent = ActionAgentOnDDIA.objects.filter(
            Q(notam__unit__aerodrome=sourcestructure) |  Q(aic__unit__aerodrome=sourcestructure) | Q(suppaip__unit__aerodrome=sourcestructure), 
            prev_state=PENDING_ADMISSION_STATE
        )
    data = ActionAgentOnDDIASerializer(actionsagent, many=True, context={'request': request}).data
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsVerifier])
def listDDIA_processed_for_sourceverifier_view(request, type_ddia):
    agent = Agent.objects.select_related('source_structure').get(user = request.user)
    sourcestructure = agent.source_structure
    actionsagent = []
    if type_ddia == 'notam':
        actionsagent = ActionAgentOnDDIA.objects.filter(
            notam__unit__aerodrome=sourcestructure, prev_state=PENDING_VERIFICATION_STATE)
    elif type_ddia == 'suppaip':
        actionsagent = ActionAgentOnDDIA.objects.filter(
            suppaip__unit__aerodrome=sourcestructure, prev_state=PENDING_VERIFICATION_STATE)
    elif type_ddia == 'aic':
        actionsagent = ActionAgentOnDDIA.objects.filter(
            aic__unit__aerodrome=sourcestructure, prev_state=PENDING_VERIFICATION_STATE)
    else:
        actionsagent = ActionAgentOnDDIA.objects.filter(
            Q(notam__unit__aerodrome=sourcestructure) |  Q(aic__unit__aerodrome=sourcestructure) | Q(suppaip__unit__aerodrome=sourcestructure), 
            prev_state=PENDING_ADMISSION_STATE
        )
    data = ActionAgentOnDDIASerializer(actionsagent, many=True, context={'request': request}).data
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

