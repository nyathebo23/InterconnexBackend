from inspect import indentsize
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

utc=pytz.UTC

class DemandeNOTAMItemListSerializer(serializers.HyperlinkedModelSerializer):
    unit_name = serializers.SerializerMethodField(read_only=True)
    airport_name = serializers.SerializerMethodField(read_only=True)
    type_ddia = serializers.SerializerMethodField(read_only=True) 
    class Meta:
        model = DemandeNOTAM
        fields = [
            'type_ddia',
            'unit_name', 
            'airport_name', 
            'url', 
            'type_notam', 
            'start_val_period', 
            'end_val_period', 
            'validity_period_type',
            'deposit_datetime', 
            'ident_ddia', 
            'state', 
            'descriptive_text', 
        ]

    def get_unit_name(self, obj):
        return obj.unit.name 
    
    def get_airport_name(self, obj):
        return obj.unit.aerodrome.name

    def get_type_ddia(self, obj):
        return 'NOTAM'

class DemandeSUPPItemListSerializer(serializers.HyperlinkedModelSerializer):
    unit_name = serializers.SerializerMethodField(read_only=True)
    airport_name = serializers.SerializerMethodField(read_only=True)
    type_ddia = serializers.SerializerMethodField(read_only=True) 
    class Meta:
        model = DemandeSUPP
        fields = [
            'type_ddia',
            'unit_name', 
            'airport_name', 
            'url', 
            'type_suppaip', 
            'start_val_period', 
            'end_val_period', 
            'period_type',
            'deposit_datetime', 
            'ident_ddia', 
            'state', 
            'descriptive_text', 
            'object'
        ]

    def get_unit_name(self, obj):
        return obj.unit.name 
    
    def get_airport_name(self, obj):
        return obj.unit.aerodrome.name

    def get_type_ddia(self, obj):
        return 'SUPP AIP'

class DemandeAICItemListSerializer(serializers.HyperlinkedModelSerializer):
    unit_name = serializers.SerializerMethodField(read_only=True)
    airport_name = serializers.SerializerMethodField(read_only=True)   
    type_ddia = serializers.SerializerMethodField(read_only=True) 
    class Meta:
        model = DemandeAIC
        fields = [
            'type_ddia',
            'unit_name', 
            'airport_name', 
            'url', 'subject', 
            'object', 
            'deposit_datetime', 
            'ident_ddia', 
            'state', 
            'descriptive_text'
        ]

    def get_unit_name(self, obj):
        return obj.unit.name 
    
    def get_airport_name(self, obj):
        return obj.unit.aerodrome.name

    def get_type_ddia(self, obj):
        return 'AIC'

class CustomDDIARelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, DemandeNOTAM):
            serializer = DemandeNOTAMItemListSerializer(value, context=self.context)
        elif isinstance(value, DemandeSUPP):
            serializer = DemandeSUPPItemListSerializer(value, context=self.context)
        elif isinstance(value, DemandeAIC):
            serializer = DemandeAICItemListSerializer(value, context=self.context)
        return serializer.data


class SourceStructureActionSerializer(serializers.ModelSerializer):
    ddia_object = CustomDDIARelatedField(read_only=True)
    class Meta:
        model = SourceStructureAction
        fields = ['ddia_object', 'prev_state', 'date_time', 'new_state']

class LocalInformerActionSerializer(serializers.ModelSerializer):
    ddia_object = CustomDDIARelatedField(read_only=True)
    class Meta:
        model = LocalInformerAction
        fields = ['ddia_object', 'date_time', 'prev_state', 'new_state']

class NationalInformerActionSerializer(serializers.ModelSerializer):
    ddia_object = CustomDDIARelatedField(read_only=True)
    class Meta:
        model = NationalInformerAction
        fields = ['ddia_object', 'date_time', 'new_state']

def make_identddia_property(aerodrome: Aerodrome, prefix: str):
    today = datetime.now()
    locationInd = aerodrome.location_ind
    inc = 0
    histor = None
    if prefix == 'AIC':
        last = DemandeAIC.objects.last()
        if last is None:
            return prefix+'-'+locationInd + '-'+ str(today.year) + '-' + str(inc).zfill(4)
        histor = DDIAHistory.objects.filter(aic=last, type_action=CREATE_ACTION) 
    elif prefix == 'NOT':
        last = DemandeNOTAM.objects.last()
        if last is None:
            return prefix+'-'+locationInd + '-'+ str(today.year) + '-' + str(inc).zfill(4)
        histor = DDIAHistory.objects.filter(notam=last, type_action=CREATE_ACTION)
    elif prefix == 'SUP':
        last = DemandeSUPP.objects.last()
        if last is None:
            return prefix+'-'+locationInd + '-'+ str(today.year) + '-' + str(inc).zfill(4)
        histor = DDIAHistory.objects.filter(suppaip=last, type_action=CREATE_ACTION)
    if histor is not None and histor.exists() and histor.first().date_time.year == today.year:
        inc = int(last.ident_ddia.split('-')[3])+1
    identddia = prefix+'-'+locationInd + '-'+ str(today.year) + '-' + str(inc).zfill(4)
    return identddia


class DemandeNOTAMForCreateUpdateSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True)
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
        attachs = validated_data.pop("attachments")
        identnotam = make_identddia_property(aerodrome, 'NOT')
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
        if datetime.today().replace(tzinfo=utc) > value.replace(tzinfo=utc):
            raise serializers.ValidationError("this date cannot be earlier than the current date") 
        return value

    def validate_end_val_period(self, value):
        start_val_period = datetime.strptime(self.initial_data['start_val_period'], "%Y-%m-%dT%H:%M:%S")
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
        if datetime.today().replace(tzinfo=utc) > value.replace(tzinfo=utc):
            raise serializers.ValidationError("this date cannot be earlier than the current date") 
        return value

    def validate_end_val_period(self, value):
        start_val_period = datetime.strptime(self.initial_data['start_val_period'], "%Y-%m-%dT%H:%M:%S")
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

