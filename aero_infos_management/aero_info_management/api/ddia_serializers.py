from .pusher_utils_actions import *
from inspect import indentsize
from django.utils import timezone
from os import read
from django.contrib.contenttypes import fields
from rest_framework import request, serializers
from ..models import *
from ..constants import *
from django.db.models import Q
from datetime import datetime, date, tzinfo
from django.contrib.auth import get_user_model
from .serializers import *
from .agents_serializers import DDIAHistorySerializer
import pytz
from django.db import transaction

utc=pytz.UTC
notam_type = ContentType.objects.get_for_model(DemandeNOTAM)
suppaip_type = ContentType.objects.get_for_model(DemandeSUPP)
aic_type = ContentType.objects.get_for_model(DemandeAIC)

def make_identddia_property(aerodrome: Aerodrome, prefix: str):
    today = datetime.now()
    locationInd = aerodrome.location_ind
    inc = 0
    histor = None
    if prefix == 'AIC':
        histor = DDIAHistory.objects.filter(ddia_type=aic_type, type_action=CREATE_ACTION).last()
        if histor is None:
            return prefix+'-'+locationInd + '-'+ str(today.year) + '-' + str(inc).zfill(4)
        last = DemandeAIC.objects.get(id=histor.id_object)
    elif prefix == 'NOT':
        histor = DDIAHistory.objects.filter(ddia_type=aic_type, type_action=CREATE_ACTION).last()
        if histor is None:
            return prefix+'-'+locationInd + '-'+ str(today.year) + '-' + str(inc).zfill(4)
        histor = DDIAHistory.objects.filter(ddia_type=notam_type, type_action=CREATE_ACTION).last()
        last = DemandeNOTAM.objects.get(id=histor.id_object)

    elif prefix == 'SUP':
        histor = DDIAHistory.objects.filter(ddia_type=aic_type, type_action=CREATE_ACTION).last()
        if histor is None:
            return prefix+'-'+locationInd + '-'+ str(today.year) + '-' + str(inc).zfill(4)
        last = DemandeSUPP.objects.get(id=histor.id_object)
    if histor is not None and histor.date_time.year == today.year:
        inc = int(last.ident_ddia.split('-')[3])+1
    identddia = prefix+'-'+locationInd + '-'+ str(today.year) + '-' + str(inc).zfill(4)
    return identddia


class DemandeNOTAMForCreateUpdateSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, required=False)
    class Meta:
        model = DemandeNOTAM
        exclude = ['initiator', 'unit', 'location_indicator']

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        agent = Agent.objects.select_related('unit__aerodrome').filter(user=user).first()
        if agent is not None:
            unit = agent.unit
            aerodrome = unit.aerodrome
        else:
            agent = LocalAgent.objects.select_related('localinformer__unit__aerodrome').get(user=user)
            unit = agent.localinformer.unit
            aerodrome = unit.aerodrome
        attachs = validated_data.pop("attachments", [])
        identnotam = make_identddia_property(aerodrome, 'NOT')
        with transaction.atomic():
            demandeNOTAM = DemandeNOTAM.objects.create(**validated_data, ident_ddia=identnotam, initiator=user, 
            unit=unit, location_indicator=aerodrome.location_ind)
            Attachment.objects.bulk_create(
                Attachment(**{"file": attach['file'], "ddia_object": demandeNOTAM}) for attach in attachs
            )
            history = DDIAHistory.objects.create(type_action=CREATE_ACTION, agent_object=agent, ddia_object=demandeNOTAM)
            return demandeNOTAM

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def validate_start_val_period(self, value):
        if timezone.now() > value:
            raise serializers.ValidationError("this date cannot be earlier than the current date") 
        return value

    def validate_end_val_period(self, value):
        start_val_period = datetime.strptime(self.initial_data['start_val_period'], "%Y-%m-%dT%H:%M:%S.%fz")
        if start_val_period.replace(tzinfo=utc) >= value.replace(tzinfo=utc):
            raise serializers.ValidationError("this date cannot be earlier than the start period date") 
        return value

    def validate_daily_freq_end(self, value):
        daily_freq_start = datetime.strptime(self.initial_data['daily_freq_start'], "%H:%M:%S").time()
        if daily_freq_start > value:
            raise serializers.ValidationError("the end time of the daily period cannot be earlier than the start time")            
        return value


class DemandeSUPPForCreateUpdateSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True)
    class Meta:
        model = DemandeSUPP
        exclude = ['initiator', 'unit', 'location_indicator']

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        agent = Agent.objects.select_related('unit__aerodrome').filter(user=user).first()
        if agent is not None:
            unit = agent.unit
            aerodrome = unit.aerodrome
        else:
            agent = LocalAgent.objects.select_related('localinformer__unit__aerodrome').get(user=user)
            unit = agent.localinformer.unit
            aerodrome = unit.aerodrome        
        attachs = validated_data.pop("attachments")
        identsupp = make_identddia_property(aerodrome, 'SUP')
        with transaction.atomic():
            demandeSUPP = DemandeSUPP.objects.create(**validated_data, ident_ddia=identsupp, initiator=user, unit=unit, 
            location_indicator=aerodrome.location_ind)
            
            Attachment.objects.bulk_create(
                Attachment(**{"file": attach['file'], "ddia_object": demandeSUPP}) for attach in attachs
            )        
            history = DDIAHistory.objects.create(type_action=CREATE_ACTION,  agent_object=agent, ddia_object=demandeSUPP)
            return demandeSUPP

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def validate_start_val_period(self, value):
        if timezone.now() > value:
            raise serializers.ValidationError("this date cannot be earlier than the current date") 
        return value

    def validate_end_val_period(self, value):
        start_val_period = datetime.strptime(self.initial_data['start_val_period'], "%Y-%m-%dT%H:%M:%S.%fz")
        if start_val_period.replace(tzinfo=utc) >= value.replace(tzinfo=utc):
            raise serializers.ValidationError("this date cannot be earlier than the start period date") 
        return value


class DemandeAICForCreateUpdateSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True)
    class Meta:
        model = DemandeAIC
        exclude = ['initiator', 'unit', 'location_indicator']

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        agent = Agent.objects.select_related('unit__aerodrome').filter(user=user).first()
        if agent is not None:
            unit = agent.unit
            aerodrome = unit.aerodrome
        else:
            agent = LocalAgent.objects.select_related('localinformer__unit__aerodrome').get(user=user)
            unit = agent.localinformer.unit
            aerodrome = unit.aerodrome   
        attachs = validated_data.pop("attachments")
        identaic = make_identddia_property(aerodrome, 'AIC')
        with transaction.atomic():
            demandeAIC = DemandeAIC.objects.create(**validated_data, ident_ddia=identaic, initiator=user, 
            unit=unit, location_indicator=aerodrome.location_ind)
            Attachment.objects.bulk_create(
            Attachment(**{"file": attach['file'], "ddia_object": demandeAIC}) for attach in attachs
            )        
            history = DDIAHistory.objects.create(type_action=CREATE_ACTION, agent_object=agent, ddia_object=demandeAIC)
            return demandeAIC

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class DemandeNOTAMSerializer(serializers.ModelSerializer):
    initiator_infos = UserSerializer(read_only=True)
    attachments = AttachmentSerializer(read_only=True, many=True)
    unit = UnitSerializer(read_only=True)
    history = DDIAHistorySerializer(read_only=True, many=True)

    class Meta:
        model = DemandeNOTAM
        fields = '__all__'


class DemandeSUPPSerializer(serializers.ModelSerializer):
    initiator_infos = UserSerializer(read_only=True)
    attachments = AttachmentSerializer(read_only=True, many=True)
    unit = UnitSerializer(read_only=True)
    history = DDIAHistorySerializer(read_only=True, many=True)

    class Meta:
        model = DemandeSUPP
        fields = '__all__'


class DemandeAICSerializer(serializers.ModelSerializer):
    initiator_infos = UserSerializer(read_only=True)
    attachments = AttachmentSerializer(read_only=True, many=True)
    unit = UnitSerializer(read_only=True)
    history = DDIAHistorySerializer(read_only=True, many=True)
    class Meta:
        model = DemandeAIC
        fields = '__all__'

