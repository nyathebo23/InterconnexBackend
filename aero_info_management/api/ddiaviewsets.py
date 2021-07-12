from .permissions import CanInitiateDDIA, IsLocalInformer, IsNationalInformer, IsOwner, IsSourceCommander, IsVerifier
from django.core.checks import messages
from rest_framework import generics, mixins , response, status, views, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from .serializers import *
from ..constants import *
from django.db.models import Q

class DDIAGenericViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [IsAuthenticated, CanInitiateDDIA]
        elif self.action == 'partial-update':
            permission_classes = [IsAuthenticated, IsOwner]
        elif self.action == 'retrieve':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes ]

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}

    def list(self, request):
        resp = {'message': 'List function is not offered in this path.'}
        return response.Response(resp, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk=None):
        resp = {'message': 'Update function is not offered in this path.'}
        return response.Response(resp, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        resp = {'message': 'Delete function is not offered in this path.'}
        return response.Response(resp, status=status.HTTP_403_FORBIDDEN) 

class DDIAControl:
    def submit_control(self, ddia, user, agent, data):
        next_state = PENDING_VERIFICATION_STATE if data['decision'] == 'submit' else CANCELLED_STATE
        if agent.user.role == SOURCE_VERIFIER and next_state == PENDING_VERIFICATION_STATE:
            next_state = PENDING_ADMISSION_STATE
        ddia.state = next_state
        ddia.save()
        ActionAgentOnDDIA.objects.create(agent=agent, prev_state=DRAFT_STATE, new_state=next_state, ddia_object=ddia)
        hist = DDIAHistory.objects.create(user=user, type_action=CONTROLE_ACTION, ddia_object=ddia)
        DDIAModifHistory.objects.create(history=hist, prev_value=DRAFT_STATE, new_value=next_state, field='state') 

    def verify_control(self, ddia, user, agent, data):
        next_state = PENDING_ADMISSION_STATE if data['decision'] == 'accept' else NON_CONFORMING_STATE
        ddia.state = next_state
        ddia.save()
        ActionAgentOnDDIA.objects.create(agent=agent, prev_state=PENDING_VERIFICATION_STATE, new_state=next_state, ddia_object=ddia)
        hist = DDIAHistory.objects.create(user=user, type_action=CONTROLE_ACTION, ddia_object=ddia)
        DDIAModifHistory.objects.create(history=hist, prev_value=PENDING_VERIFICATION_STATE, new_value=next_state, field='state')
        if data['decision'] != 'accept':
            RequestReferral.objects.create(user=user, message=data['message'], ddia_object=ddia)   

    def admit_control(self, ddia, user, agent, data):
        next_state = PENDING_VALIDATION_STATE if data['decision'] == 'accept' else NOT_ADMITTED_STATE
        ddia.state = next_state
        ddia.save()
        ActionAgentOnDDIA.objects.create(agent=agent, prev_state=PENDING_ADMISSION_STATE, new_state=next_state, ddia_object=ddia)
        hist = DDIAHistory.objects.create(user=user, type_action=CONTROLE_ACTION, ddia_object=ddia)
        DDIAModifHistory.objects.create(history=hist, prev_value=PENDING_ADMISSION_STATE, new_value=next_state, field='state')
        if data['decision'] != 'accept':
            RequestReferral.objects.create(user=user, message=data['message'], ddia_object=ddia)       

    def validate_control(self, ddia, user, agent, data):
        next_state = PENDING_APPROVAL_STATE if data['decision'] == 'accept' else NOT_VALIDATED_STATE
        ddia.state = next_state
        ddia.save()
        Validation.objects.create(local_agent=agent, new_state=next_state, ddia_object=ddia)
        hist = DDIAHistory.objects.create(user=user, type_action=CONTROLE_ACTION, ddia_object=ddia)
        DDIAModifHistory.objects.create(history=hist, prev_value=PENDING_VALIDATION_STATE, new_value=next_state, field='state')
        if data['decision'] != 'accept':
            RequestReferral.objects.create(user=user, message=data['message'], ddia_object=ddia)    

    def approve_control(self, ddia, user, agent, data):
        next_state = PENDING_ADMISSION_STATE if data['decision'] == 'accept' else NON_CONFORMING_STATE
        ddia.state = next_state
        ddia.save()
        Approbation.objects.create(national_agent=agent, new_state=next_state, ddia_object=ddia)
        hist = DDIAHistory.objects.create(user=user, type_action=CONTROLE_ACTION, ddia_object=ddia)
        DDIAModifHistory.objects.create(history=hist, prev_value=PENDING_APPROVAL_STATE, new_value=next_state, field='state')
        if data['decision'] != 'accept':
            RequestReferral.objects.create(user=user, message=data['message'], ddia_object=ddia)      


class DemandeAICViewSet(DDIAGenericViewSet):
    queryset = DemandeAIC.objects.all()
    serializer_class = DemandeAICForCreateSerializer

class DemandeNOTAMViewSet(DDIAGenericViewSet):
    queryset = DemandeNOTAM.objects.all()
    serializer_class = DemandeNOTAMForCreateSerializer

class DemandeSUPPViewSet(DDIAGenericViewSet):
    queryset = DemandeSUPP.objects.all()
    serializer_class = DemandeSUPPForCreateSerializer


class DDIAControlViewset(viewsets.ViewSet, DDIAControl):

    def get_permissions(self):
        if self.action == 'submittoverif':
            return [IsAuthenticated(), IsOwner()]
        elif self.action == 'verify':
            return [IsAuthenticated(), IsVerifier()]
        elif self.action == 'admit':
            return [IsAuthenticated(), IsSourceCommander()]
        elif self.action == 'validate':
            return [IsAuthenticated(), IsLocalInformer()]
        elif self.action == 'approve':
            return [IsAuthenticated(), IsNationalInformer()]
        
        return [IsAuthenticated()]
        
    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated, IsOwner])
    def submittoverif(self, request, type_ddia, pk, format='json'):
        self.check_permissions(request)
        user, data = request.user, request.data
        type_ddia = self.kwargs.get('type_ddia')
        DDIAType = ContentType.objects.get(app_label='aero_info_management', model=type_ddia)
        ddia = DDIAType.get_object_for_this_type(id=pk)
        ddia.deposit_datetime = datetime.now() 
        self.check_object_permissions(request, ddia)
        agent = Agent.objects.get(user=user)   
        self.submit_control(ddia, user, agent, data)
        return response.Response({'message': 'Ok'}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated, IsVerifier])
    def verify(self, request, type_ddia, pk, format='json'):
        self.check_permissions(request)
        user, data = request.user, request.data
        type_ddia = self.kwargs.get('type_ddia')
        DDIAType = ContentType.objects.get(app_label='aero_info_management', model=type_ddia)
        ddia = DDIAType.get_object_for_this_type(id=pk) 
        self.check_object_permissions(request, ddia)
        agent = Agent.objects.get(user=user)   
        self.verify_control(ddia, user, agent, data)
        return response.Response({'message': 'Ok'}, status=status.HTTP_200_OK)
     
    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated, IsSourceCommander])
    def admit(self, request, type_ddia, pk, format='json'):
        self.check_permissions(request)
        user, data = request.user, request.data
        type_ddia = self.kwargs.get('type_ddia')
        DDIAType = ContentType.objects.get(app_label='aero_info_management', model=type_ddia)
        ddia = DDIAType.get_object_for_this_type(id=pk) 
        self.check_object_permissions(request, ddia)
        agent = Agent.objects.get(user=user)   
        self.admit_control(ddia, user, agent, data)
        return response.Response({'message': 'Ok'}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated, IsLocalInformer])
    def validate(self, request, type_ddia, pk, format='json'):
        self.check_permissions(request)
        user, data = request.user, request.data
        type_ddia = self.kwargs.get('type_ddia')
        DDIAType = ContentType.objects.get(app_label='aero_info_management', model=type_ddia)
        ddia = DDIAType.get_object_for_this_type(id=pk)         
        self.check_object_permissions(request, ddia)
        agent = LocalAgent.objects.get(user=user)   
        self.validate_control(ddia, user, agent, data)
        return response.Response({'message': 'Ok'}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated, IsNationalInformer])
    def approve(self, request, type_ddia, pk, format='json'):
        self.check_permissions(request)
        user, data = request.user, request.data
        type_ddia = self.kwargs.get('type_ddia')
        DDIAType = ContentType.objects.get(app_label='aero_info_management', model=type_ddia)
        ddia = DDIAType.get_object_for_this_type(id=pk)        
        self.check_object_permissions(request, ddia)
        agent = NationalAgent.objects.get(user=user)   
        self.approve_control(ddia, user, agent, data)
        return response.Response({'message': 'Ok'}, status=status.HTTP_200_OK)     
