import random
from aero_infos_management.celery import app
from .models import *
import pusher
from .api.serializers import *
from .constants import *

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

@app.task
def notify_unit_at_date_for_suppaip(id_supp):
    suppaip = DemandeSUPP.objects.get(id=id_supp)
    unit = suppaip.unit
    notification = Notification.objects.create(receiver_object=unit, event='ddia-validity-exp', 
    new_ddia_state=PENDING_PUBLICATION_STATE, ddia_type='SUPP AIP', ref_ddia=suppaip.ident_ddia)
    pusher_client.trigger('unit'+str(unit.id), 'ddia-validity-exp', data = {
        'notification': NotificationSerializer(notification).data,
        'expiration_date': str(suppaip.end_val_period)
    })   

@app.task
def notify_unit_at_date_for_notam(id_notam):
    notam = DemandeNOTAM.objects.get(id=id_notam)
    unit = notam.unit
    notification = Notification.objects.create(receiver_object=unit, event='ddia-validity-exp', 
    new_ddia_state=PENDING_PUBLICATION_STATE, ddia_type='NOTAM', ref_ddia=notam.ident_ddia)
    pusher_client.trigger('unit'+str(unit.id), 'ddia-validity-exp', data = {
        'notification': NotificationSerializer(notification).data,
        'expiration_date': str(notam.end_val_period)
    })    

@app.task
def notify_two_days_after_approbation(ddia, type_ddia, nationalinformer, localinformer=None):
    channels = ['inf-nat'+nationalinformer.id]
    if localinformer is not None:
        notification = Notification.objects.create(receiver_object=localinformer, event='ddia-must-be-published', 
        new_ddia_state=PENDING_PUBLICATION_STATE, ddia_type=typeDDIADict.get(type_ddia), ref_ddia=ddia.ident_ddia)
        channels.append('inf-loc'+localinformer.id)
    notification = Notification.objects.create(receiver_object=ddia.unit, event='ddia-must-be-published', 
    new_ddia_state=PENDING_PUBLICATION_STATE, ddia_type=typeDDIADict.get(type_ddia), ref_ddia=ddia.ident_ddia)
    pusher_client.trigger(channels, 'ddia-must-be-published', data = {
        'notification': NotificationSerializer(notification).data
    })