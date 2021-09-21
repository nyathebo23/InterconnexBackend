import re
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from .permissions import *
from rest_framework import generics, mixins, response, status, views, viewsets
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
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


notam_type = ContentType.objects.get_for_model(DemandeNOTAM)
suppaip_type = ContentType.objects.get_for_model(DemandeSUPP)
aic_type = ContentType.objects.get_for_model(DemandeAIC)

class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 15
    def get_paginated_response(self, data):
        return response.Response({
            'counts': self.page.paginator.count,
            'results': data
        }, status=status.HTTP_200_OK)

def render_pagination_ddia_queryset(queryset: QuerySet, request: HttpRequest, state: str, date_order: str):
    queryfiltered = queryset if state == 'all' else queryset.filter(state=state)
    queryfiltered = queryfiltered if date_order == 'ascendingDate' else list(reversed(queryfiltered))
    paginator = Paginator(queryfiltered, PAGE_DDIA_LIST_SIZE)
    print(len(queryfiltered), paginator.count)

    page = request.GET.get('page')
    try:
        result_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        result_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        result_page = paginator.page(paginator.num_pages)
    return result_page, paginator.count 


def render_pagination_localinf_response(queryset: QuerySet, request: HttpRequest):
    paginator = Paginator(queryset, PAGE_DDIA_LIST_SIZE)
    page = request.GET.get('page')
    try:
        result_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        result_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        result_page = paginator.page(paginator.num_pages)
    data = LocalInformerActionSerializer(result_page, many=True, context={'request': request}).data
    return response.Response({
        'counts': paginator.count,
        'results': data
    }, status=status.HTTP_200_OK)

def render_pagination_aerodromeagent_response(queryset: QuerySet, request: HttpRequest):
    paginator = Paginator(queryset, PAGE_DDIA_LIST_SIZE)
    page = request.GET.get('page')
    try:
        result_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        result_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        result_page = paginator.page(paginator.num_pages)
    data = SourceStructureActionSerializer(result_page, many=True, context={'request': request}).data
    return response.Response({
                'counts': paginator.count,
                'results': data
            }, status=status.HTTP_200_OK)

def render_pagination_nationalinf_response(queryset: QuerySet, request: HttpRequest):
    paginator = Paginator(queryset, PAGE_DDIA_LIST_SIZE)
    page = request.GET.get('page')
    try:
        result_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        result_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        result_page = paginator.page(paginator.num_pages)
    data = NationalInformerActionSerializer(result_page, many=True, context={'request': request}).data
    return response.Response({
                'counts': paginator.count,
                'results': data
            }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsNationalInformer])
def listDDIA_inwaiting_for_nationalinf_view(request, type_ddia):
    date_order = request.GET.get('date_order')
    national_agent = NationalAgent.objects.select_related('nationalinformer').get(user=request.user)
    nationalinf = national_agent.nationalinformer
    validations = []
    if type_ddia == 'notam':
        validations = LocalInformerAction.objects.filter(notam__state=PENDING_APPROVAL_STATE, target_nationalinf=nationalinf)
    elif type_ddia == 'suppaip':
        validations = LocalInformerAction.objects.filter(suppaip__state=PENDING_APPROVAL_STATE, target_nationalinf=nationalinf)
    elif type_ddia == 'aic':
        validations = LocalInformerAction.objects.filter(aic__state=PENDING_APPROVAL_STATE, target_nationalinf=nationalinf)
    else:
        validations = LocalInformerAction.objects.filter(
            Q(aic__state=PENDING_APPROVAL_STATE) | Q(notam__state=PENDING_APPROVAL_STATE) | Q(suppaip__state=PENDING_APPROVAL_STATE),
            target_nationalinf=nationalinf
        )
    validations = validations if date_order == 'ascendingDate' else list(reversed(validations))
    data = LocalInformerActionSerializer(validations, many=True, context={'request': request}).data
    return response.Response({'counts': None, 'results': data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAuthorityLocalInformer])
def listDDIA_inwaiting_for_authoritylocalinformer_view(request, type_ddia):
    date_order = request.GET.get('date_order')
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

    actionsagent = actionsagent if date_order == 'ascendingDate' else list(reversed(actionsagent))       
    data = SourceStructureActionSerializer(actionsagent, many=True, context={'request': request}).data
    return response.Response({'counts': None, 'results': data}, status=status.HTTP_200_OK)
   

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSourceCommander])
def listDDIA_inwaiting_for_sourcestructure_view(request, type_ddia):
    has_localinf = request.GET.get('from_localinf') == 'yes'
    date_order = request.GET.get('date_order')
    agent = Agent.objects.select_related('aerodrome').get(user = request.user)
    aerodrome = agent.aerodrome
    actionsagent = []
    if has_localinf:
        if type_ddia == 'notam':
            actionsagent = LocalInformerAction.objects.filter(notam__unit__aerodrome=aerodrome, notam__state=PENDING_ADMISSION_STATE)
        elif type_ddia == 'suppaip':
            actionsagent = LocalInformerAction.objects.filter(suppaip__unit__aerodrome=aerodrome, suppaip__state=PENDING_ADMISSION_STATE)
        elif type_ddia == 'aic':
            actionsagent = LocalInformerAction.objects.filter(aic__unit__aerodrome=aerodrome, aic__state=PENDING_ADMISSION_STATE)
        else:
            actionsagent = LocalInformerAction.objects.filter(
            Q(notam__unit__aerodrome=aerodrome, notam__state=PENDING_ADMISSION_STATE) 
            | Q(aic__unit__aerodrome=aerodrome, aic__state=PENDING_ADMISSION_STATE) 
            | Q(suppaip__unit__aerodrome=aerodrome, suppaip__state=PENDING_ADMISSION_STATE), 
            )
        actionsagent = actionsagent if date_order == 'ascendingDate' else list(reversed(actionsagent))
        data = SourceStructureActionSerializer(actionsagent, many=True, context={'request': request}).data
        return response.Response({'counts': None, 'results': data}, status=status.HTTP_200_OK)
    else:
        if type_ddia == 'notam':
            actionsagent = SourceStructureAction.objects.filter(notam__unit__aerodrome=aerodrome, notam__state=PENDING_ADMISSION_STATE)
        elif type_ddia == 'suppaip':
            actionsagent = SourceStructureAction.objects.filter(suppaip__unit__aerodrome=aerodrome, suppaip__state=PENDING_ADMISSION_STATE)
        elif type_ddia == 'aic':
            actionsagent = SourceStructureAction.objects.filter(aic__unit__aerodrome=aerodrome, aic__state=PENDING_ADMISSION_STATE)
        else:
            actionsagent = SourceStructureAction.objects.filter(
            Q(notam__unit__aerodrome=aerodrome, notam__state=PENDING_ADMISSION_STATE) 
            | Q(aic__unit__aerodrome=aerodrome, aic__state=PENDING_ADMISSION_STATE) 
            | Q(suppaip__unit__aerodrome=aerodrome, suppaip__state=PENDING_ADMISSION_STATE), 
            )
        actionsagent = actionsagent if date_order == 'ascendingDate' else list(reversed(actionsagent))
        data = LocalInformerActionSerializer(actionsagent, many=True, context={'request': request}).data
        return response.Response({'counts': None, 'results': data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsVerifier])
def listDDIA_inwaiting_for_sourceverifier_view(request, type_ddia):
    date_order = request.GET.get('date_order')
    islocalinf = request.GET.get('is_localinf') == 'yes'
    user = request.user
    if islocalinf:
        aerodrome = LocalAgent.objects.get(user=user).localinformer.aerodrome
    else:
        aerodrome = Agent.objects.get(user=user).aerodrome
    actionsagent = []
    if type_ddia == 'notam':
        actionsagent = SourceStructureAction.objects.filter(notam__unit__aerodrome=aerodrome,  notam__state=PENDING_VERIFICATION_STATE)
    elif type_ddia == 'suppaip':
        actionsagent = SourceStructureAction.objects.filter(suppaip__unit__aerodrome=aerodrome,  suppaip__state=PENDING_VERIFICATION_STATE)
    elif type_ddia == 'aic':
        actionsagent = SourceStructureAction.objects.filter(aic__unit__aerodrome=aerodrome,  aic__state=PENDING_VERIFICATION_STATE)
    else:
        actionsagent = SourceStructureAction.objects.filter(
           Q(notam__unit__aerodrome=aerodrome,  notam__state=PENDING_VERIFICATION_STATE) 
         | Q(aic__unit__aerodrome=aerodrome,  aic__state=PENDING_VERIFICATION_STATE) 
         | Q(suppaip__unit__aerodrome=aerodrome,  suppaip__state=PENDING_VERIFICATION_STATE), 
        )
    actionsagent = actionsagent if date_order == 'ascendingDate' else list(reversed(actionsagent))
    data = SourceStructureActionSerializer(actionsagent, many=True, context={'request': request}).data
    return response.Response({'counts': None, 'results': data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def listDDIA_inwaiting_for_initiator_view(request):
    try:
        agent = Agent.objects.select_related('unit').get(user = request.user)
        ownunit = agent.unit
    except:
        agent = LocalAgent.objects.select_related('localinformer__unit').get(user = request.user)
        ownunit = agent.localinformer.unit
    demandes_notam = DemandeNOTAM.objects.filter(unit=ownunit).filter(state__in=[NON_CONFORMING_STATE, NOT_ADMITTED_STATE, NOT_VALIDATED_STATE, NOT_APPROVED_STATE])
    data_notam = DemandeNOTAMItemListSerializer(demandes_notam, many=True, context={'request': request}).data
    demandes_suppaip = DemandeSUPP.objects.filter(unit=ownunit).filter(state__in=[NON_CONFORMING_STATE, NOT_ADMITTED_STATE, NOT_VALIDATED_STATE, NOT_APPROVED_STATE])
    data_supp = DemandeSUPPItemListSerializer(demandes_suppaip, many=True, context={'request': request}).data
    demandes_aic = DemandeAIC.objects.filter(unit=ownunit).filter(state__in=[NON_CONFORMING_STATE, NOT_ADMITTED_STATE, NOT_VALIDATED_STATE, NOT_APPROVED_STATE])
    data_aic = DemandeAICItemListSerializer(demandes_aic, many=True, context={'request': request}).data  
    data = {
        'demandesAIC': data_aic,
        'demandesNOTAM': data_notam,
        'demandesSUPP': data_supp
    }  
    return response.Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsNationalInformer])
def listDDIA_processed_for_nationalinf_view(request, type_ddia):
    state, date_order = request.GET.get('state'), request.GET.get('date_order')
    national_agent = NationalAgent.objects.select_related('nationalinformer').get(user=request.user)
    nationalinf = national_agent.nationalinformer
    approbations = []
    if type_ddia == 'notam':
        approbations = NationalInformerAction.objects.filter(ddia_type=notam_type, prev_state=PENDING_APPROVAL_STATE)
        approbations = approbations if state == 'all' else approbations.filter(notam__state=state) 
    elif type_ddia == 'suppaip':
        approbations = NationalInformerAction.objects.filter(ddia_type=suppaip_type, prev_state=PENDING_APPROVAL_STATE)
        approbations = approbations if state == 'all' else approbations.filter(suppaip__state=state) 
    elif type_ddia == 'aic':
        approbations = NationalInformerAction.objects.filter(ddia_type=aic_type, prev_state=PENDING_APPROVAL_STATE)
        approbations = approbations if state == 'all' else approbations.filter(aic__state=state) 
    else:
        approbations = NationalInformerAction.objects.all()
        if not nationalinf.is_authority:
            approbations = approbations.filter(national_agent__nationalinformer=nationalinf)
    approbations = approbations if state == 'all' else approbations.filter(
       Q(notam__state=state) | Q(suppaip__state=state) | Q(aic__state=state), prev_state=PENDING_APPROVAL_STATE
    ) 
    approbations = approbations if date_order == 'ascendingDate' else list(reversed(approbations))
    return render_pagination_nationalinf_response(approbations, request)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAuthorityLocalInformer])
def listDDIA_processed_for_authoritylocalinformer_view(request, type_ddia):
    state, date_order = request.GET.get('state'), request.GET.get('date_order')
    local_agent = LocalAgent.objects.select_related('localinformer').get(user=request.user)
    localinf = local_agent.localinformer
    validations = []
    if type_ddia == 'notam':
        validations = LocalInformerAction.objects.filter(local_agent__localinformer=localinf, ddia_type=notam_type, prev_state=PENDING_VALIDATION_STATE)
        validations = validations if state == 'all' else validations.filter(notam__state=state)
    elif type_ddia == 'suppaip':
        validations = LocalInformerAction.objects.filter(local_agent__localinformer=localinf, ddia_type=suppaip_type, prev_state=PENDING_VALIDATION_STATE)
        validations = validations if state == 'all' else validations.filter(suppaip__state=state)
    elif type_ddia == 'aic':
        validations = LocalInformerAction.objects.filter(local_agent__localinformer=localinf, ddia_type=aic_type, prev_state=PENDING_VALIDATION_STATE)
        validations = validations if state == 'all' else validations.filter(aic__state=state)
    else:
        validations = LocalInformerAction.objects.filter(local_agent__localinformer=localinf,  prev_state=PENDING_VALIDATION_STATE)
        validations = validations if state == 'all' else validations.filter(
        Q(notam__state=state) | Q(suppaip__state=state) | Q(aic__state=state) ) 
    validations = validations if date_order == 'ascendingDate' else list(reversed(validations))
    return render_pagination_localinf_response(validations, request)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSourceCommander])
def listDDIA_processed_for_sourcestructure_view(request, type_ddia):
    state, date_order = request.GET.get('state'), request.GET.get('date_order')
    agent = Agent.objects.select_related('aerodrome').get(user = request.user)
    aerodrome = agent.aerodrome
    actionsagent = []
    if type_ddia == 'notam':
        actionsagent = SourceStructureAction.objects.filter(notam__unit__aerodrome=aerodrome,  prev_state=PENDING_ADMISSION_STATE)
        actionsagent = actionsagent if state == 'all' else actionsagent.filter(notam__state=state)
    elif type_ddia == 'suppaip':
        actionsagent = SourceStructureAction.objects.filter(suppaip__unit__aerodrome=aerodrome,  prev_state=PENDING_ADMISSION_STATE)
        actionsagent = actionsagent if state == 'all' else actionsagent.filter(suppaip__state=state)
    elif type_ddia == 'aic':
        actionsagent = SourceStructureAction.objects.filter(aic__unit__aerodrome=aerodrome,  prev_state=PENDING_ADMISSION_STATE)
        actionsagent = actionsagent if state == 'all' else actionsagent.filter(aic__state=state)
    else:
        actionsagent = SourceStructureAction.objects.filter(
            Q(notam__unit__aerodrome=aerodrome) |  Q(aic__unit__aerodrome=aerodrome) | Q(suppaip__unit__aerodrome=aerodrome), 
            prev_state=PENDING_ADMISSION_STATE
        )
        actionsagent = actionsagent if state == 'all' else actionsagent.filter(
            Q(notam__state=state) | Q(suppaip__state=state) | Q(aic__state=state) 
        )
    actionsagent = actionsagent if date_order == 'ascendingDate' else list(reversed(actionsagent))
    return render_pagination_aerodromeagent_response(actionsagent, request)



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsVerifier])
def listDDIA_processed_for_source_localinformer_view(request, type_ddia):
    user, state, date_order = request.user, request.GET.get('state'), request.GET.get('date_order')
    localagent = LocalAgent.objects.select_related('localinformer__aerodrome').get(user = user)
    aerodrome = localagent.localinformer.aerodrome
    actionsagent = []
    if type_ddia == 'notam':
        actionsagent = LocalInformerAction.objects.filter(notam__unit__aerodrome=aerodrome,  prev_state=PENDING_VERIFICATION_STATE)
        actionsagent = actionsagent if state == 'all' else actionsagent.filter(notam__state=state)
    elif type_ddia == 'suppaip':
        actionsagent = LocalInformerAction.objects.filter(suppaip__unit__aerodrome=aerodrome,  prev_state=PENDING_VERIFICATION_STATE)
        actionsagent = actionsagent if state == 'all' else actionsagent.filter(suppaip__state=state)
    elif type_ddia == 'aic':
        actionsagent = LocalInformerAction.objects.filter(aic__unit__aerodrome=aerodrome,  prev_state=PENDING_VERIFICATION_STATE)
        actionsagent = actionsagent if state == 'all' else actionsagent.filter(aic__state=state)
    else:
        actionsagent = LocalInformerAction.objects.filter(
            Q(notam__unit__aerodrome=aerodrome) |  Q(aic__unit__aerodrome=aerodrome) | Q(suppaip__unit__aerodrome=aerodrome), 
            prev_state=PENDING_VERIFICATION_STATE
        )
        actionsagent = actionsagent if state == 'all' else actionsagent.filter(Q(notam__state=state) | Q(suppaip__state=state) | Q(aic__state=state) )
    actionsagent = actionsagent if date_order == 'ascendingDate' else list(reversed(actionsagent))
    return render_pagination_localinf_response(actionsagent, request)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsVerifier])
def listDDIA_processed_for_sourceverifier_view(request, type_ddia):
    user, state, date_order = request.user, request.GET.get('state'), request.GET.get('date_order')
    agent = Agent.objects.select_related('aerodrome').get(user = user)
    aerodrome = agent.aerodrome
    actionsagent = []
    if type_ddia == 'notam':
        actionsagent = SourceStructureAction.objects.filter(notam__unit__aerodrome=aerodrome,  prev_state=PENDING_ADMISSION_STATE)
        actionsagent = actionsagent if state == 'all' else actionsagent.filter(notam__state=state)
    elif type_ddia == 'suppaip':
        actionsagent = SourceStructureAction.objects.filter(suppaip__unit__aerodrome=aerodrome,  prev_state=PENDING_ADMISSION_STATE)
        actionsagent = actionsagent if state == 'all' else actionsagent.filter(suppaip__state=state)
    elif type_ddia == 'aic':
        actionsagent = SourceStructureAction.objects.filter(aic__unit__aerodrome=aerodrome,  prev_state=PENDING_ADMISSION_STATE)
        actionsagent = actionsagent if state == 'all' else actionsagent.filter(aic__state=state)
    else:
        actionsagent = SourceStructureAction.objects.filter(
            Q(notam__unit__aerodrome=aerodrome) |  Q(aic__unit__aerodrome=aerodrome) | Q(suppaip__unit__aerodrome=aerodrome), 
            prev_state=PENDING_ADMISSION_STATE
        )
        actionsagent = actionsagent if state == 'all' else actionsagent.filter(Q(notam__state=state) | Q(suppaip__state=state) | Q(aic__state=state))
    actionsagent = actionsagent if date_order == 'ascendingDate' else list(reversed(actionsagent))
    return render_pagination_aerodromeagent_response(actionsagent, request)


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanInitiateDDIA])
def listDDIA_processed_for_initiator_view(request, type_ddia):
    state, date_order = request.GET.get('state'), request.GET.get('date_order')
    try:
        agent = Agent.objects.select_related('unit').get(user = request.user)
        ownunit = agent.unit
    except:
        agent = LocalAgent.objects.select_related('localinformer__unit').get(user = request.user)
        ownunit = agent.localinformer.unit
    data, count = [], 0
    if type_ddia == 'notam':
        demandes_notam = DemandeNOTAM.objects.filter(unit=ownunit)
        demandes_notam, count = render_pagination_ddia_queryset(demandes_notam, request, state, date_order)
        data = DemandeNOTAMItemListSerializer(demandes_notam, many=True, context={'request': request}).data
    elif type_ddia == 'suppaip':
        demandes_suppaip = DemandeSUPP.objects.filter(unit=ownunit) 
        demandes_suppaip, count = render_pagination_ddia_queryset(demandes_suppaip, request, state, date_order)
        data = DemandeSUPPItemListSerializer(demandes_suppaip, many=True, context={'request': request}).data
    elif type_ddia == 'aic':
        demandes_aic = DemandeAIC.objects.filter(unit=ownunit)  
        demandes_aic, count = render_pagination_ddia_queryset(demandes_aic, request, state, date_order)
        data = DemandeAICItemListSerializer(demandes_aic, many=True, context={'request': request}).data
    return response.Response({
        'counts': count,
        'results': data
    }, status=status.HTTP_200_OK)


class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    def get_serializer_class(self):
        if self.action == 'get' or self.action == 'list':
            return AgentSerializerExtend
        return AgentSerializer
    http_method_names = ['get', 'post', 'head']

class LocalAgentViewSet(viewsets.ModelViewSet):
    queryset = LocalAgent.objects.all()
    def get_serializer_class(self):
        if self.action == 'get':
            return LocalAgentSerializerExtend
        return LocalAgentSerializer
    http_method_names = ['get', 'post', 'head']

class NationalAgentViewSet(viewsets.ModelViewSet):
    queryset = NationalAgent.objects.all()
    def get_serializer_class(self):
        if self.action == 'get':
            return NationalAgentSerializerExtend
        return NationalAgentSerializer    
    http_method_names = ['get', 'post', 'head']

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UnitSerializer
    http_method_names = ['get', 'post', 'put', 'head', 'patch', 'delete']

class AerodromeViewSet(viewsets.ModelViewSet):
    queryset = Aerodrome.objects.all()
    def get_permissions(self):
        if self.action == 'retrieve' and self.request.GET.get('extend') is not None and self.request.user.role != SOURCE_AGENT:
            return [IsAuthenticated()]
        if self.action == 'list'  and self.request.user.role != SOURCE_AGENT:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminUser()]
    def get_serializer_class(self):
        if self.action == 'list' and self.request.GET.get('extend') is not None:
            return AerodromeExtendSerializer
        return AerodromeSerializer
    http_method_names = ['get', 'post', 'put', 'head', 'patch', 'delete']

class LocalInformerViewSet(viewsets.ModelViewSet):
    queryset = LocalInformer.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = LocalInformerSerializer 
    http_method_names = ['get', 'post', 'put', 'head', 'patch', 'delete']

    def get_queryset(self):
        if self.action == 'get' and self.request.GET.get('extern') is not None:
            localinfs = LocalInformer.objects.filter(aerodrome=None, unit=None)
            return localinfs
        return LocalInformer.objects.all()
        
class NationalInformerViewSet(viewsets.ModelViewSet):
    queryset = NationalInformer.objects.all()

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated(), IsAdminUser()]            
    serializer_class = NationalInformerSerializer
    http_method_names = ['get', 'post', 'put', 'head', 'patch', 'delete']


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSourceCommander])
def get_target_nationalinformer(request, type_ddia, id):
    agent = Agent.objects.get(user=request.user)
    DDIAType = ContentType.objects.get(app_label='aero_info_management', model=type_ddia)
    aerodrome = agent.aerodrome
    if aerodrome.is_conceded:
        action = LocalInformerAction.objects.filter(ddia_type=DDIAType, object_id=id, new_state=PENDING_ADMISSION_STATE).last()
        nationalinf = action.target_nationalinf
        data = NationalInformerSerializer(nationalinf).data
        return response.Response(data, status=status.HTTP_200_OK)
    return response.Response({'data': 'No nationalinformer found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_localagent_infos(request):
    localagent = LocalAgent.objects.filter(user=request.user).first()
    if localagent is not None:
        data = LocalAgentSerializerExtend(localagent).data
        return response.Response(data=data, status=status.HTTP_200_OK)
    return response.Response("No Local agent object with this user found", status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_agent_infos(request):
    agent = Agent.objects.filter(user=request.user).first()
    if agent is not None:
        data = AgentSerializerExtend(agent).data
        return response.Response(data=data, status=status.HTTP_200_OK)
    localagent = LocalAgent.objects.filter(user=request.user).first()
    if localagent is not None:
        data = LocalAgentSerializerExtend(localagent).data
        return response.Response(data=data, status=status.HTTP_200_OK)  
    return response.Response("No agent object with this user found", status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsNationalInformer])
def get_nationalagent_infos(request):
    nationalagent = NationalAgent.objects.filter(user=request.user).first()
    if nationalagent is not None:
        data = NationalAgentSerializerExtend(nationalagent).data
        return response.Response(data=data, status=status.HTTP_200_OK)
    return response.Response("No National agent object with this user found", status=status.HTTP_404_NOT_FOUND)    

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_user(request, pk):
    user = User.objects.filter(id=pk).first()
    if user is not None:
        user.delete()
        return response.Response({"message": "User with Id {} deleted successfully".format(id) }, status=status.HTTP_204_NO_CONTENT)
    return response.Response("No User object with this user's id found", status=status.HTTP_404_NOT_FOUND)   


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
