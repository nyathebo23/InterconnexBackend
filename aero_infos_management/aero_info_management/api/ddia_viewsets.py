import re
from .pusher_utils_actions import *
from ..tasks import *
from django.db import transaction
from django.http.request import HttpRequest
from .permissions import *
from django.core.checks import messages
from rest_framework import generics, mixins , response, status, views, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework import filters
from .serializers import *
from .ddia_serializers import *
from ..constants import *
from django.db.models import Q
from django.utils import timezone
from ..pdf_generator import *
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from ..pdf_generator import generate
from django.core.mail import EmailMessage
from django.conf import settings

def send_mail_to_publisher(mail: str):
    try:
        mail_subject = 'DEMANDE DE PUBLICATION'

        message = 'Transmission de demande de diffusion'
        email = EmailMessage(
            mail_subject, message, from_email=settings.EMAIL_HOST_USER, to=[mail]
        )
        # set type to html
        email.content_subtype = "html"
        email.attach_file('./files/ddia.pdf')
        email.send()
    except:
        print('could not send mail')


class DDIAGenericViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [IsAuthenticated, CanInitiateDDIA]
        elif self.action == 'partial-update' or self.action == 'update':
            permission_classes = [IsAuthenticated, IsOwner]
        elif self.action == 'retrieve':
            permission_classes = [IsAuthenticated, CanReadDDIA]
        return [permission() for permission in permission_classes ]

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}

    def list(self, request: HttpRequest):
        resp = {'message': 'List function is not offered in this path.'}
        return response.Response(resp, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request: HttpRequest, pk=None):
        resp = {'message': 'Delete function is not offered in this path.'}
        return response.Response(resp, status=status.HTTP_403_FORBIDDEN) 

class DDIAControl:
    def submit_control(self, ddia, agent, data, typeDDIA, islocalinf: bool, request):
        next_state = PENDING_VERIFICATION_STATE
        if agent.user.role == SOURCE_VERIFIER:
            next_state = PENDING_ADMISSION_STATE
        ddia.state = next_state
        ddia.save()
        unit = ddia.unit
        aerodrome = unit.aerodrome
        if islocalinf:
            nationalinf = NationalInformer.objects.get(id=data['nationalinf_id'])
            action = LocalInformerAction.objects.create(local_agent=agent, prev_state=DRAFT_STATE, new_state=next_state, 
            ddia_object=ddia, target_nationalinf=nationalinf)
            notify_sourcestructure_ddia_submission(action, typeDDIA, aerodrome, ddia.ident_ddia, request)
            # notify_sourceverifier_after_action(next_state, ddia, aerodrome, typeDDIA)
        else:
            action = SourceStructureAction.objects.create(agent=agent, prev_state=DRAFT_STATE, new_state=next_state, ddia_object=ddia)
            if next_state == PENDING_ADMISSION_STATE:
                notify_sourcestructure_ddia_submission(action, typeDDIA, aerodrome, ddia.ident_ddia, request)
            elif next_state == PENDING_VERIFICATION_STATE:
                notify_sourceverifier_ddia_submission(action, typeDDIA, aerodrome, ddia.ident_ddia, request)
        notify_sourceunit_after_action(next_state, ddia.ident_ddia, ddia.unit, typeDDIA)
        hist = DDIAHistory.objects.create(agent_object=agent, type_action=CONTROLE_ACTION, ddia_object=ddia)
        DDIAModifHistory.objects.create(history=hist, prev_value=DRAFT_STATE, new_value=next_state, field='state') 

    def cancel_ddia(self, ddia, agent, typeDDIA, islocalinf: bool):
        prevstate = ddia.state
        ddia.state = CANCELLED_STATE
        ddia.save()
        if islocalinf:
            action = LocalInformerAction.objects.create(local_agent=agent, prev_state=prevstate, new_state=CANCELLED_STATE, ddia_object=ddia)
        else:
            action = SourceStructureAction.objects.create(agent=agent, prev_state=prevstate, new_state=CANCELLED_STATE, ddia_object=ddia)    
        notify_sourceunit_after_action(CANCELLED_STATE, ddia.ident_ddia, ddia.unit, typeDDIA)
        hist = DDIAHistory.objects.create(agent_object=agent, type_action=CONTROLE_ACTION, ddia_object=ddia)
        DDIAModifHistory.objects.create(history=hist, prev_value=prevstate, new_value=CANCELLED_STATE, field='state')
        return action

    def verify_localinf_control(self, ddia, agent, data):
        next_state = PENDING_ADMISSION_STATE if data['decision'] == 'accept' else NON_CONFORMING_STATE
        ddia.state = next_state
        ddia.save()
        nationalinf = None if next_state == NON_CONFORMING_STATE or data.get('nationalinf_id') is None else NationalInformer.objects.get(id=data['nationalinf_id'])
        action = LocalInformerAction.objects.create(local_agent=agent, prev_state=PENDING_VERIFICATION_STATE, new_state=next_state, ddia_object=ddia, target_nationalinf=nationalinf)        
        hist = DDIAHistory.objects.create(agent_object=agent, type_action=CONTROLE_ACTION, ddia_object=ddia)
        DDIAModifHistory.objects.create(history=hist, prev_value=PENDING_VERIFICATION_STATE, new_value=next_state, field='state')
        if data['decision'] != 'accept':
            RequestReferral.objects.create(agent_object=agent, message=data['message'], ddia_object=ddia)   
        return action

    def verify_control(self, ddia, agent, data):
        next_state = PENDING_ADMISSION_STATE if data['decision'] == 'accept' else NON_CONFORMING_STATE
        ddia.state = next_state
        ddia.save()
        action = SourceStructureAction.objects.create(agent=agent, prev_state=PENDING_VERIFICATION_STATE, new_state=next_state, ddia_object=ddia)
        hist = DDIAHistory.objects.create(agent_object=agent, type_action=CONTROLE_ACTION, ddia_object=ddia)
        DDIAModifHistory.objects.create(history=hist, prev_value=PENDING_VERIFICATION_STATE, new_value=next_state, field='state')
        if data['decision'] != 'accept':
            RequestReferral.objects.create(agent_object=agent, message=data['message'], ddia_object=ddia)   
        return action

    def admit_control(self, ddia, agent, has_localinf, data):
        if data['decision'] == 'accept':
            if has_localinf and data['afterapprove'] == 'yes':
                next_state = PENDING_APPROVAL_STATE
            else:
                next_state = PENDING_VALIDATION_STATE
        else:
            next_state = NOT_ADMITTED_STATE
        ddia.state = next_state
        ddia.save()
        action = SourceStructureAction.objects.create(agent=agent, prev_state=PENDING_ADMISSION_STATE, new_state=next_state, ddia_object=ddia)
        hist = DDIAHistory.objects.create(agent_object=agent, type_action=CONTROLE_ACTION, ddia_object=ddia)
        DDIAModifHistory.objects.create(history=hist, prev_value=PENDING_ADMISSION_STATE, new_value=next_state, field='state')
        if data['decision'] != 'accept':
            RequestReferral.objects.create(agent_object=agent, message=data['message'], ddia_object=ddia)       
        return action

    def validate_control(self, ddia, agent, data):
        next_state = PENDING_APPROVAL_STATE if data['decision'] == 'accept' else NOT_VALIDATED_STATE
        ddia.state = next_state
        ddia.save()
        nationalinf = NationalInformer.objects.filter(is_authority=True).first()
        action = LocalInformerAction.objects.create(local_agent=agent, prev_state=PENDING_VALIDATION_STATE, new_state=next_state, ddia_object=ddia, target_nationalinf=nationalinf)
        hist = DDIAHistory.objects.create(agent_object=agent, type_action=CONTROLE_ACTION, ddia_object=ddia)
        DDIAModifHistory.objects.create(history=hist, prev_value=PENDING_VALIDATION_STATE, new_value=next_state, field='state')
        if data['decision'] != 'accept':
            RequestReferral.objects.create(agent_object=agent, message=data['message'], ddia_object=ddia)    
        return action
    
    def approve_control(self, ddia, agent, data):
        next_state = PENDING_PUBLICATION_STATE if data['decision'] == 'accept' else NOT_APPROVED_STATE
        ddia.state = next_state
        ddia.save()
        action = NationalInformerAction.objects.create(national_agent=agent, new_state=next_state, ddia_object=ddia)
        hist = DDIAHistory.objects.create(agent_object=agent, type_action=CONTROLE_ACTION, ddia_object=ddia)
        DDIAModifHistory.objects.create(history=hist, prev_value=PENDING_APPROVAL_STATE, new_value=next_state, field='state')
        if data['decision'] != 'accept':
            RequestReferral.objects.create(agent_object=agent, message=data['message'], ddia_object=ddia)      
        return action

    def published_control(self, ddia, agent, data):
        ddia.state = PUBLISHED_STATE
        ddia.publication_code = data['publication_code']
        ddia.save()
        if isinstance(agent, LocalAgent):
            action = LocalInformerAction.objects.create(local_agent=agent, prev_state=PENDING_PUBLICATION_STATE, new_state=PUBLISHED_STATE, ddia_object=ddia)
        elif isinstance(agent, NationalAgent):
            action = NationalInformerAction.objects.create(national_agent=agent, new_state=PUBLISHED_STATE, ddia_object=ddia)
        hist = DDIAHistory.objects.create(agent_object=agent, type_action=CONTROLE_ACTION, ddia_object=ddia)
        DDIAModifHistory.objects.create(history=hist, prev_value=PENDING_PUBLICATION_STATE, new_value=PUBLISHED_STATE, field='state')   
        return action


class DemandeAICViewSet(DDIAGenericViewSet):
    parser_classes = [MultiPartParser]
    queryset = DemandeAIC.objects.all()
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial-update']:
            return DemandeAICForCreateUpdateSerializer
        elif self.action == 'retrieve':
            return DemandeAICSerializer
        return DemandeAICSerializer

    def perform_create(self, serializer):
        demandeAIC: DemandeAIC = serializer.save()
        notify_sourceunit_ddia_creation(demandeAIC, 'demandeaic', self.request)
        return demandeAIC

class DemandeNOTAMViewSet(DDIAGenericViewSet):
    parser_classes = [MultiPartParser]
    queryset = DemandeNOTAM.objects.all()
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial-update']:
            return DemandeNOTAMForCreateUpdateSerializer
        elif self.action == 'retrieve':
            return DemandeNOTAMSerializer
        return DemandeNOTAMSerializer

    def perform_create(self, serializer):
        demandeNOTAM: DemandeNOTAM = serializer.save()
        # notify_sourceunit_ddia_creation(demandeNOTAM, 'demandenotam', self.request)        
        return demandeNOTAM

class DemandeSUPPViewSet(DDIAGenericViewSet):
    parser_classes = [MultiPartParser]
    queryset = DemandeSUPP.objects.all()
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial-update']:
            return DemandeSUPPForCreateUpdateSerializer
        elif self.action == 'retrieve':
            return DemandeSUPPSerializer
        return DemandeSUPPSerializer

    def perform_create(self, serializer):
        demandeSUPP: DemandeSUPP = serializer.save()
        notify_sourceunit_ddia_creation(demandeSUPP, 'demandesupp', self.request)        
        return demandeSUPP


class DDIAControlViewset(viewsets.ViewSet, DDIAControl):

    def get_permissions(self):
        if self.action == 'submittoverif':
            return [IsAuthenticated(), IsOwner()]
        elif self.action == 'verify':
            return [IsAuthenticated(), IsVerifier()]
        elif self.action == 'admit':
            return [IsAuthenticated(), IsSourceCommander()]
        elif self.action == 'validate':
            return [IsAuthenticated(), IsAuthorityLocalInformer()]
        elif self.action == 'approve':
            return [IsAuthenticated(), IsNationalInformer()]
        
        return [IsAuthenticated()]
        
    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated, IsOwner])
    def submittoverif(self, request: HttpRequest, type_ddia, pk, format='json'):
        self.check_permissions(request)
        user, data = request.user, request.data
        type_ddia = self.kwargs.get('type_ddia')
        DDIAType = ContentType.objects.get(app_label='aero_info_management', model=type_ddia)
        ddia = DDIAType.get_object_for_this_type(id=pk)
        date = timezone.now() + timedelta(seconds=3630)
        ddia.deposit_datetime = timezone.now() 
        self.check_object_permissions(request, ddia)
        agent, isLocalInf = Agent.objects.filter(user=user).first(), False 
        try:
            if agent is None:  
                agent, isLocalInf = LocalAgent.objects.get(user=user), True
            with transaction.atomic():
                self.submit_control(ddia, agent, data, type_ddia, isLocalInf, request)
        except Exception as e:
            return response.Response('Excepion: {}'.format(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response.Response({'message': 'Ok'}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated, IsOwner])
    def cancel(self, request: HttpRequest, type_ddia, pk, format='json'):
        self.check_permissions(request)
        user = request.user
        type_ddia = self.kwargs.get('type_ddia')
        DDIAType = ContentType.objects.get(app_label='aero_info_management', model=type_ddia)
        ddia = DDIAType.get_object_for_this_type(id=pk)
        ddia.deposit_datetime = datetime.now() 
        self.check_object_permissions(request, ddia)
        agent, isLocalInf = Agent.objects.filter(user=user).first(), False 
        try:
            if agent is None:  
                agent, isLocalInf = LocalAgent.objects.get(user=user), True
            with transaction.atomic():
                self.cancel_ddia(ddia, agent, type_ddia, isLocalInf)
        except Exception as e:
            return response.Response('Excepion: {}'.format(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response.Response({'message': 'Ok'}, status=status.HTTP_200_OK)


    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated, IsVerifier])
    def verify(self, request: HttpRequest, type_ddia, pk, format='json'):
        islocalinf = request.GET.get('is_localinf') == 'yes'
        self.check_permissions(request)
        user, data = request.user, request.data 
        if data.get('decision') not in [ACCEPT, REJECT]:
            return response.Response({'message': 'Error in request data decision on ddia control'}, status=status.HTTP_400_BAD_REQUEST)
        type_ddia = self.kwargs.get('type_ddia')
        DDIAType = ContentType.objects.get(app_label='aero_info_management', model=type_ddia)
        ddia = DDIAType.get_object_for_this_type(id=pk) 
        aerodrome = ddia.unit.aerodrome
        self.check_object_permissions(request, ddia)
        try:
            with transaction.atomic(): 
                if islocalinf:
                    agent = LocalAgent.objects.get(user=user)
                    action = self.verify_localinf_control(ddia, agent, data)
                else:
                    agent = Agent.objects.get(user=user)  
                    action = self.verify_control(ddia, agent, data)
                if action.new_state == PENDING_ADMISSION_STATE:
                    notify_sourcestructure_ddia_verification(action, type_ddia, aerodrome, ddia.ident_ddia, request)
                notify_sourceverifier_after_action(action.new_state, ddia, aerodrome, type_ddia)
        except Exception as e:
            return response.Response('Excepion: {}'.format(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response.Response({'message': 'Ok'}, status=status.HTTP_200_OK)
     
    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated, IsSourceCommander])
    def admit(self, request: HttpRequest, type_ddia, pk, format='json'):
        from_localinf = request.GET.get('from_localinf') == 'yes'
        self.check_permissions(request)
        user, data = request.user, request.data
        if data.get('decision') not in [ACCEPT, REJECT]:
            return response.Response({'message': 'Error in request data decision on ddia control'}, status=status.HTTP_400_BAD_REQUEST)
        type_ddia = self.kwargs.get('type_ddia')
        DDIAType = ContentType.objects.get(app_label='aero_info_management', model=type_ddia)
        ddia = DDIAType.get_object_for_this_type(id=pk) 
        self.check_object_permissions(request, ddia)
        agent = Agent.objects.select_related('aerodrome').get(user=user) 
        aerodrome = agent.aerodrome  
        try:
            with transaction.atomic():
                action = self.admit_control(ddia, agent, from_localinf, data)
                if action.new_state == PENDING_APPROVAL_STATE:
                    localinf_action = LocalInformerAction.objects.select_related('target_nationalinf').filter(object_id=ddia.id, new_state=PENDING_ADMISSION_STATE).last()
                    nationalinf = localinf_action.target_nationalinf
                    notify_nationalinf_ddia_sourcecommand_admission(action, type_ddia, nationalinf, ddia.ident_ddia, request)
                elif action.new_state == PENDING_VALIDATION_STATE:
                    localinf = LocalInformer.objects.filter(aerodrome=None).first()
                    notify_localinf_ddia_sourcecommand_admission(action, type_ddia, localinf, ddia.ident_ddia, request)
                notify_sourcecommand_after_action(action.new_state, ddia, aerodrome, type_ddia)
        except Exception as e:
            return response.Response('Excepion: {}'.format(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response.Response({'message': 'Ok'}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated, IsAuthorityLocalInformer])
    def validate(self, request: HttpRequest, type_ddia, pk, format='json'):
        self.check_permissions(request)
        user, data = request.user, request.data
        if data.get('decision') not in [ACCEPT, REJECT]:
            return response.Response({'message': 'Error in request data decision on ddia control'}, status=status.HTTP_400_BAD_REQUEST)
        type_ddia = self.kwargs.get('type_ddia')
        DDIAType = ContentType.objects.get(app_label='aero_info_management', model=type_ddia)
        ddia = DDIAType.get_object_for_this_type(id=pk)         
        self.check_object_permissions(request, ddia)
        agent = LocalAgent.objects.select_related('localinformer').get(user=user)
        localinf = agent.localinformer
        try:
            with transaction.atomic():
                action = self.validate_control(ddia, agent, data)
                if action.new_state == PENDING_APPROVAL_STATE:
                    notify_nationalinf_ddia_localinf_validation(action, type_ddia, ddia.ident_ddia, request)
                else:
                    pass
                notify_localinformer_after_action(action.new_state, ddia, localinf, type_ddia)
        except Exception as e:
            return response.Response('Excepion: {}'.format(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response.Response({'message': 'Ok'}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated, IsNationalInformer])
    def approve(self, request: HttpRequest, type_ddia, pk, format='json'):
        self.check_permissions(request)
        user, data = request.user, request.data
        if data.get('decision') not in [ACCEPT, REJECT]:
            return response.Response({'message': 'Error in request data decision on ddia control'}, status=status.HTTP_400_BAD_REQUEST)
        type_ddia = self.kwargs.get('type_ddia')
        DDIAType = ContentType.objects.get(app_label='aero_info_management', model=type_ddia)
        ddia = DDIAType.get_object_for_this_type(id=pk)        
        self.check_object_permissions(request, ddia)
        agent = NationalAgent.objects.select_related('nationalinformer').get(user=user)  
        nationalinf = agent.nationalinformer
        try:
            with transaction.atomic(): 
                action = self.approve_control(ddia, agent, data)
                if action.new_state == PENDING_PUBLICATION_STATE:
                    if not nationalinf.is_authority:
                        notify_nationalinf_ddia_nationalinf_approbation(action, type_ddia, ddia.ident_ddia, request)
                    else:
                        is_generated = generate(ddia, type_ddia)
                        if is_generated:
                            send_mail_to_publisher('franckhebo@gmail.com')
                    action_validate = LocalInformerAction.objects.select_related('local_agent__localinformer').filter(
                        object_id=ddia.pk, new_state=PENDING_APPROVAL_STATE).first()
                    args_func = [ddia, type_ddia, nationalinf]
                    if action_validate:
                        args_func.append(action_validate.local_agent.localinformer)
                    datenotif = action.date_time + timedelta(days=2)

                notify_nationalinformer_after_action(action.new_state, ddia, nationalinf, type_ddia)

        except Exception as e:
            return response.Response('Excepion: {}'.format(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
        return response.Response({'message': 'Ok'}, status=status.HTTP_200_OK)     

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated])
    def set_published(self, request: HttpRequest, type_ddia, pk, format='json'):
        self.check_permissions(request)
        user, data = request.user, request.data
        type_ddia = self.kwargs.get('type_ddia')
        DDIAType = ContentType.objects.get(app_label='aero_info_management', model=type_ddia)
        ddia = DDIAType.get_object_for_this_type(id=pk)        
        self.check_object_permissions(request, ddia)
        agent = LocalAgent.objects.select_related('localinformer').filter(user=user).first()  
        if agent is None:
            agent = NationalAgent.objects.select_related('nationalinformer').get(user=user)
        self.published_control(ddia, agent, data)
        action_validate = LocalInformerAction.objects.select_related('target_nationalinf').filter(object_id=ddia.pk, new_state=PENDING_APPROVAL_STATE).first()
        if action_validate is not None:
            nationalinf = action_validate.target_nationalinf 
            notify_nationalinformer_after_action(PUBLISHED_STATE, ddia, nationalinf, type_ddia)
        if type_ddia == 'demandenotam' and ddia.type_notam != NOTAMC:
            period_type = ddia.validity_period_type
            nbdays_before = 5
            datenotif = ddia.end_val_period - timedelta(days=nbdays_before)
            notify_unit_at_date_for_notam.apply_async((pk,), eta=datenotif)
        elif type_ddia == 'demandesupp':
            nbdays_before = 5
            datenotif = ddia.end_val_period - timedelta(days=nbdays_before) 
            notify_unit_at_date_for_suppaip.apply_async((pk,), eta=datenotif)

        # try:
        #     with transaction.atomic(): 
        #         self.published_control(ddia, agent, data)
        #         action_validate = LocalInformerAction.objects.select_related('target_nationalinf').filter(object_id=ddia.pk, new_state=PENDING_APPROVAL_STATE).first()
        #         if action_validate is not None:
        #             nationalinf = action_validate.target_nationalinf 
        #             notify_nationalinformer_after_action(PUBLISHED_STATE, ddia, nationalinf, type_ddia)
        #         if type_ddia == 'demandenotam' and ddia.type_notam != NOTAMC:
        #             period_type = ddia.validity_period_type
        #             nbdays_before = 5
        #             datenotif = ddia.end_val_period - timedelta(days=nbdays_before)
        #             # schedule(
        #             #     'aero_info_management.api.pusher_utils_actions.notify_unit_at_date_for_notam', args=[ddia], schedule_type='D', next_run = datenotif, repeats = 2
        #             # )
        #             scheduler.add_job(notify_unit_at_date_for_notam, args=[ddia], next_run_time=datenotif)
        #             scheduler.start()
        #         elif type_ddia == 'demandesupp':
        #             nbdays_before = 5
        #             datenotif = ddia.end_val_period - timedelta(days=nbdays_before) 
        #             # schedule(
        #             #     'aero_info_management.api.pusher_utils_actions.notify_unit_at_date_for_suppaip', args=[ddia], schedule_type='D', next_run = datenotif, repeats = 2
        #             # )
        #             scheduler.add_job(notify_unit_at_date_for_suppaip, args=[ddia], next_run_time=datenotif)
        #             scheduler.start()

        # except Exception as e:
        #     return response.Response('Excepion: {}'.format(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
 
        return response.Response({'message': 'Ok'}, status=status.HTTP_200_OK)   