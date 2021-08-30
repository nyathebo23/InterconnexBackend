from os import error

from rest_framework import response, status
from .permissions import CanInitiateDDIA, IsAuthorityLocalInformer, IsNationalInformer, IsSourceCommander, IsVerifier
from django.http.request import HttpRequest
from rest_framework.permissions import IsAuthenticated
from ..models import Aerodrome, LocalInformer, LocalInformerAction, NationalInformer, Notification, Unit
from .serializers import *
import pusher
from rest_framework.decorators import api_view, permission_classes, action

pusher_client = pusher.Pusher(
  app_id='1249385',
  key='2f4ec77a435984938284',
  secret='00d91d8bbb2d98a229c8',
  cluster='eu',
  ssl=True
)

typeDDIADict: dict = {
    'demandenotam': 'NOTAM',
    'demandeaic': 'AIC',
    'demandesupp': 'SUPP AIP'
}

def notify_sourceunit_ddia_creation(ddiaObj, typeDDIA: str, request):
    unit = ddiaObj.unit
    notification = Notification.objects.create(receiver_object=unit, new_ddia_state=ddiaObj.state,
    event='ddia-creation', ddia_type=typeDDIADict.get(typeDDIA), ref_ddia=ddiaObj.ident_ddia)
    data = None
    if typeDDIA == 'demandenotam':
        data = DemandeNOTAMItemListSerializer(ddiaObj, context={'request': request}).data
    elif typeDDIA == 'demandesupp':
        data = DemandeSUPPItemListSerializer(ddiaObj, context={'request': request}).data
    elif typeDDIA == 'demandeaic':
        data = DemandeAICItemListSerializer(ddiaObj, context={'request': request}).data
    pusher_client.trigger('unit'+str(unit.id), 'ddia-creation', data={
        'typeDDIA': typeDDIA,
        'data': data,
        'notification': NotificationSerializer(notification).data
    })

def notify_sourceverifier_ddia_submission(actionObj, typeDDIA: str, aerodrome: Aerodrome, refDDIA: str, request):
    notification = Notification.objects.create(receiver_object=aerodrome, event='ddia-reception-submission', 
    new_ddia_state=actionObj.new_state, ddia_type=typeDDIADict.get(typeDDIA), ref_ddia=refDDIA)
    data = SourceStructureActionSerializer(actionObj, context={'request': request}).data
    pusher_client.trigger('verif-source'+aerodrome.location_ind, 'ddia-reception-submission', data={
        'typeDDIA': typeDDIA,
        'data': data,
        'notification': NotificationSerializer(notification).data
    })

def notify_sourcestructure_ddia_submission(actionObj, typeDDIA: str, aerodrome: Aerodrome, refDDIA: str, request):
    notification = Notification.objects.create(receiver_object=aerodrome, event='ddia-reception-verifsubmission', 
    new_ddia_state=actionObj.new_state, ddia_type=typeDDIADict.get(typeDDIA), ref_ddia=refDDIA)
    if isinstance(actionObj, LocalInformerAction):
        data = LocalInformerActionSerializer(actionObj, context={'request': request}).data
    else:
        data = SourceStructureActionSerializer(actionObj, context={'request': request}).data
    pusher_client.trigger('aerodrome' + aerodrome.location_ind, 'ddia-reception-verifsubmission', data={
        'typeDDIA': typeDDIA,
        'data': data,
        'notification': NotificationSerializer(notification).data
    })

def notify_sourcestructure_ddia_verification(actionObj, typeDDIA: str, aerodrome: Aerodrome, refDDIA: str, request):
    notification = Notification.objects.create(receiver_object=aerodrome, event='ddia-reception-verification', 
    new_ddia_state=actionObj.new_state, ddia_type=typeDDIADict.get(typeDDIA), ref_ddia=refDDIA)
    if isinstance(actionObj, LocalInformerAction):
        data = LocalInformerActionSerializer(actionObj, context={'request': request}).data
    else:
        data = SourceStructureActionSerializer(actionObj, context={'request': request}).data
    pusher_client.trigger('aerodrome'+aerodrome.location_ind, 'ddia-reception-verification', data={
        'typeDDIA': typeDDIA,
        'data': data,
        'notification': NotificationSerializer(notification).data
    })

def notify_localinf_ddia_sourcecommand_admission(actionObj, typeDDIA: str, localinformer: LocalInformer, refDDIA: str, request):
    notification = Notification.objects.create(receiver_object=localinformer, event='ddia-reception-admission', 
    new_ddia_state=actionObj.new_state, ddia_type=typeDDIADict.get(typeDDIA), ref_ddia=refDDIA)
    data = SourceStructureActionSerializer(actionObj, context={'request': request}).data
    pusher_client.trigger('inf-loc'+str(localinformer.id), 'ddia-reception-admission', data={
        'typeDDIA': typeDDIA,
        'data': data,
        'notification': NotificationSerializer(notification).data
    })

def notify_nationalinf_ddia_sourcecommand_admission(actionObj, typeDDIA: str, nationalinformer: NationalInformer, refDDIA: str, request):
    notification = Notification.objects.create(receiver_object=nationalinformer, event='ddia-reception-admission', 
    new_ddia_state=actionObj.new_state, ddia_type=typeDDIADict.get(typeDDIA), ref_ddia=refDDIA)
    data = SourceStructureActionSerializer(actionObj, context={'request': request}).data
    pusher_client.trigger('inf-nat'+str(nationalinformer.id), 'ddia-reception-admission', data={
        'typeDDIA': typeDDIA,
        'data': data,
        'notification': NotificationSerializer(notification).data
    })

def notify_nationalinf_ddia_nationalinf_approbation(actionObj, typeDDIA: str, refDDIA: str, request):
    nationalinformer = NationalInformer.objects.get(is_authority=True)
    notification = Notification.objects.create(receiver_object=nationalinformer, event='ddia-signal-approbation', 
    new_ddia_state=actionObj.new_state, ddia_type=typeDDIADict.get(typeDDIA), ref_ddia=refDDIA)
    data = NationalInformerActionSerializer(actionObj, context={'request': request}).data
    pusher_client.trigger('inf-nat'+str(nationalinformer.id), 'ddia-signal-approbation', data={
        'typeDDIA': typeDDIA,
        'data': data,
        'notification': NotificationSerializer(notification).data
    })

def notify_nationalinf_ddia_localinf_validation(actionObj, typeDDIA: str, refDDIA: str, request):
    nationalinformer = NationalInformer.objects.get(is_authority=True)
    notification = Notification.objects.create(receiver_object=nationalinformer, event='ddia-reception-validation', 
    new_ddia_state=actionObj.new_state, ddia_type=typeDDIADict.get(typeDDIA), ref_ddia=refDDIA)
    data = SourceStructureActionSerializer(actionObj, context={'request': request}).data
    pusher_client.trigger('inf-nat'+str(nationalinformer.id), 'ddia-reception-validation', data={
        'typeDDIA': typeDDIA,
        'data': data,
        'notification': NotificationSerializer(notification).data
    })

def notify_sourceunit_after_action(next_state: str, refDDIA: str, unit: Unit, typeDDIA: str):
    notification = Notification.objects.create(receiver_object=unit, event='ddia-state-change', 
    new_ddia_state=next_state, ddia_type=refDDIA, ref_ddia=refDDIA)
    pusher_client.trigger('unit'+str(unit.id), 'ddia-state-change', data={
        'typeDDIA': typeDDIA,
        'notification': NotificationSerializer(notification).data
    })   

def notify_sourceverifier_after_action(next_state: str, ddia, aerodrome: Aerodrome, typeDDIA: str):
    notification = Notification.objects.create(receiver_object=aerodrome, event='ddia-state-change', 
    new_ddia_state=next_state, ddia_type=typeDDIADict.get(typeDDIA), ref_ddia=ddia.ident_ddia)
    pusher_client.trigger('verif-source'+aerodrome.location_ind, 'ddia-state-change', data={
        'typeDDIA': typeDDIA,
        'notification': NotificationSerializer(notification).data
    })  
    unit = ddia.unit 
    notify_sourceunit_after_action(next_state, ddia.ident_ddia, unit, typeDDIA)
    
def notify_sourcecommand_after_action(next_state: str, ddia, aerodrome: Aerodrome, typeDDIA: str):
    notification = Notification.objects.create(receiver_object=aerodrome, event='ddia-state-change', 
    new_ddia_state=next_state, ddia_type=typeDDIADict.get(typeDDIA), ref_ddia=ddia.ident_ddia)
    pusher_client.trigger('aerodrome'+aerodrome.location_ind, 'ddia-state-change', data={
        'typeDDIA': typeDDIA,
        'notification': NotificationSerializer(notification).data
    })   
    # notify_sourceverifier_after_action(next_state, ddia, aerodrome, typeDDIA)

def notify_localinformer_after_action(next_state: str, ddia, localinf: LocalInformer, typeDDIA: str):
    notification = Notification.objects.create(receiver_object=localinf, event='ddia-state-change', 
    new_ddia_state=next_state, ddia_type=typeDDIADict.get(typeDDIA), ref_ddia=ddia.ident_ddia)
    pusher_client.trigger('inf-loc'+str(localinf.id), 'ddia-state-change', data={
        'typeDDIA': typeDDIA,
        'notification': NotificationSerializer(notification).data
    }) 
    aerodrome = ddia.unit.aerodrome
    notify_sourcecommand_after_action(next_state, ddia, aerodrome, typeDDIA)
    notify_sourceverifier_after_action(next_state, ddia, aerodrome, typeDDIA)  


def notify_nationalinformer_after_action(next_state: str, ddia, nationalinf: NationalInformer, typeDDIA: str):
    notification = Notification.objects.create(receiver_object=nationalinf, event='ddia-state-change', 
    new_ddia_state=next_state, ddia_type=typeDDIADict.get(typeDDIA), ref_ddia=ddia.ident_ddia)
    pusher_client.trigger('inf-nat'+str(nationalinf.id), 'ddia-state-change', data={
        'typeDDIA': typeDDIA,
        'notification': NotificationSerializer(notification).data
    })
    if nationalinf.is_authority:
        localinformer = LocalInformer.objects.filter(aerodrome=None).first()
        notify_localinformer_after_action(next_state, ddia, localinformer, typeDDIA)
    else:
        aerodrome = ddia.unit.aerodrome
        nationalinf2 = NationalInformer.objects.get(is_authority=True)
        notify_sourcecommand_after_action(next_state, ddia, aerodrome, typeDDIA)
        notify_sourceverifier_after_action(next_state, ddia, aerodrome, typeDDIA)
        notification = Notification.objects.create(receiver_object=nationalinf2, event='ddia-state-change', 
        new_ddia_state=next_state, ddia_type=typeDDIADict.get(typeDDIA), ref_ddia=ddia.ident_ddia)
        pusher_client.trigger('inf-nat'+str(nationalinf2.id), 'ddia-state-change', data={
            'typeDDIA': typeDDIA,
            'notification': NotificationSerializer(notification).data
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated, CanInitiateDDIA])
def get_notifications_sourceunit(request: HttpRequest):
    agent = Agent.objects.select_related('unit').filter(user=request.user).first()
    if agent is not None:
        unit = agent.unit
    else:
        agent = LocalAgent.objects.select_related('localinformer__unit').get(user=request.user)
        unit = agent.localinformer.unit
    notifications = Notification.objects.filter(unit=unit).filter(Q(event='ddia-creation'))
    data = NotificationSerializer(notifications, many=True).data
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsVerifier])
def get_notifications_sourceverifier(request: HttpRequest):
    agent = Agent.objects.select_related('aerodrome').filter(user=request.user).first()
    if agent is not None:
        aerodrome = agent.aerodrome
    else:
        agent = LocalAgent.objects.select_related('localinformer__aerodrome').get(user=request.user)
        aerodrome = agent.localinformer.aerodrome
    notifications = Notification.objects.filter(aerodrome=aerodrome, event='ddia-reception-submission')
    data = NotificationSerializer(notifications, many=True).data
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSourceCommander])
def get_notifications_sourcecommand(request: HttpRequest):
    agent = Agent.objects.select_related('aerodrome').filter(user=request.user).first()
    aerodrome = agent.aerodrome
    notifications = Notification.objects.filter(aerodrome=aerodrome).filter(Q(event='ddia-reception-verifsubmission') | Q(event='ddia-reception-verification'))
    data = NotificationSerializer(notifications, many=True).data
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsNationalInformer])
def get_notifications_nationalinformer(request: HttpRequest):
    agent = NationalAgent.objects.select_related('nationalinformer').filter(user=request.user).first()
    nationalinf = agent.nationalinformer
    notifications = Notification.objects.filter(nationalinformer=nationalinf).filter(Q(event='ddia-signal-approbation') | Q(event='ddia-reception-validation'))
    data = NotificationSerializer(notifications, many=True).data
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAuthorityLocalInformer])
def get_notifications_localinformer(request: HttpRequest):
    agent = LocalAgent.objects.select_related('localinformer').filter(user=request.user).first()
    localinf = agent.localinformer
    notifications = Notification.objects.filter(localinformer=localinf, event='ddia-reception-admission')
    data = NotificationSerializer(notifications, many=True).data
    return response.Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mark_notif_as_read(request: HttpRequest, idNotif):
    try:
        notif = Notification.objects.get(id=idNotif)
        notif.read = True
        notif.save()
        return response.Response({'message': 'ok'}, status=status.HTTP_200_OK)
    except:
        return response.Response({'message': 'no notif with this id found'}, status=status.HTTP_404_NOT_FOUND)

