from inspect import indentsize
from os import read
from django.contrib.contenttypes import fields
from rest_framework import request, serializers
from ..models import *
from ..constants import *
from django.db.models import Q
from datetime import datetime, date

from django.contrib.auth import get_user_model

User = get_user_model()

notam_type = ContentType.objects.get_for_model(DemandeNOTAM)
suppaip_type = ContentType.objects.get_for_model(DemandeSUPP)
aic_type = ContentType.objects.get_for_model(DemandeAIC)

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'
        
class AerodromeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aerodrome
        fields = '__all__'

class LocalInformerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalInformer
        fields = '__all__'

class NationalInformerSerializer(serializers.ModelSerializer):
    class Meta:
        model = NationalInformer
        fields = '__all__'

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file']


class DemandeNOTAMItemListSerializer(serializers.HyperlinkedModelSerializer):
    unit_name = serializers.SerializerMethodField(read_only=True)
    airport_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = DemandeNOTAM
        fields = [
            'unit_name', 
            'airport_name', 
            'url', 
            'type_notam', 
            'start_val_period', 
            'end_val_period', 
            'deposit_datetime', 
            'ident_ddia', 
            'state', 
            'descriptive_text', 
        ]
    def get_unit_name(self, obj):
        return obj.unit.name 
    
    def get_airport_name(self, obj):
        return obj.unit.aerodrome.name


class DemandeSUPPItemListSerializer(serializers.HyperlinkedModelSerializer):
    unit_name = serializers.SerializerMethodField(read_only=True)
    airport_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DemandeSUPP
        fields = [
            'unit_name', 
            'airport_name', 
            'url', 'type_suppaip', 
            'start_val_period', 
            'end_val_period', 
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

class DemandeAICItemListSerializer(serializers.HyperlinkedModelSerializer):
    unit_name = serializers.SerializerMethodField(read_only=True)
    airport_name = serializers.SerializerMethodField(read_only=True)    
    class Meta:
        model = DemandeAIC
        fields = [
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

def make_identddia_property(agent: Agent, prefix: str):
    today = datetime.now()
    code_aerodrome = agent.source_structure.code
    inc = 0
    histor = None
    if prefix == 'AIC':
        last = DemandeAIC.objects.last()
        if last is None:
            return prefix+'-'+code_aerodrome + '-'+ str(today.year) + '-' + str(inc).zfill(4)
        histor = DDIAHistory.objects.filter(aic=last, type_action=CREATE_ACTION) 
    elif prefix == 'NOT':
        last = DemandeNOTAM.objects.last()
        if last is None:
            return prefix+'-'+code_aerodrome + '-'+ str(today.year) + '-' + str(inc).zfill(4)
        histor = DDIAHistory.objects.filter(notam=last, type_action=CREATE_ACTION)
    elif prefix == 'SUPP':
        last = DemandeSUPP.objects.last()
        if last is None:
            return prefix+'-'+code_aerodrome + '-'+ str(today.year) + '-' + str(inc).zfill(4)
        histor = DDIAHistory.objects.filter(suppaip=last, type_action=CREATE_ACTION)
    if histor is not None and histor.exists() and histor.first().date_time.year == today.year:
        inc = int(last.ident_ddia.split('-')[3])
    identddia = prefix+'-'+code_aerodrome + '-'+ str(today.year) + '-' + str(inc).zfill(4)
    return identddia


class DemandeNOTAMForCreateUpdateSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True)
    class Meta:
        model = DemandeNOTAM
        exclude = ['initiator', 'unit', 'location_indicator']

    def create(self, validated_data):
        request = self.context.get("request")
        agent = Agent.objects.select_related('source_structure').get(user=request.user)
        attachs = validated_data.pop("attachments")
        identnotam = make_identddia_property(agent, 'NOT')
        demandeNOTAM = DemandeNOTAM.objects.create(**validated_data, ident_ddia=identnotam, initiator=agent, 
        unit=agent.unit, location_indicator=agent.source_structure.location_ind)
        Attachment.objects.bulk_create(
            Attachment(**{"file": attach['file'], "ddia_object": demandeNOTAM}) for attach in attachs
        )
        history = DDIAHistory.objects.create(type_action=CREATE_ACTION, user=request.user, ddia_object=demandeNOTAM)
        return demandeNOTAM

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def validate_start_val_period(self, value):
        if date.today() > value:
            raise serializers.ValidationError("this date cannot be earlier than the current date") 
        return value

    def validate_end_val_period(self, value):
        start_val_period = datetime.strptime(self.initial_data['start_val_period'], "%Y-%m-%d").date()
        if start_val_period >= value:
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
        agent = Agent.objects.select_related('source_structure').get(user=request.user)
        attachs = validated_data.pop("attachments")
        identsupp = make_identddia_property(agent, 'SUP')
        demandeSUPP = DemandeSUPP.objects.create(**validated_data, ident_ddia=identsupp, initiator=agent, unit=agent.unit, 
        location_indicator=agent.source_structure.location_ind)
        
        Attachment.objects.bulk_create(
            Attachment(**{"file": attach['file'], "ddia_object": demandeSUPP}) for attach in attachs
        )        
        history = DDIAHistory.objects.create(type_action=CREATE_ACTION, user=request.user, ddia_object=demandeSUPP)
        return demandeSUPP

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def validate_start_val_period(self, value):
        if date.today() > value:
            raise serializers.ValidationError("this date cannot be earlier than the current date") 
        return value

    def validate_end_val_period(self, value):
        start_val_period = datetime.strptime(self.initial_data['start_val_period'], '%Y-%m-%d').date()
        if start_val_period >= value:
            raise serializers.ValidationError("this date cannot be earlier than the start period date") 
        return value


class DemandeAICForCreateUpdateSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True)
    class Meta:
        model = DemandeAIC
        exclude = ['initiator', 'unit', 'location_indicator']

    def create(self, validated_data):
        request = self.context.get("request")
        agent = Agent.objects.select_related('source_structure').get(user=request.user)
        attachs = validated_data.pop("attachments")
        identaic = make_identddia_property(agent, 'AIC')
        demandeAIC = DemandeAIC.objects.create(**validated_data, ident_ddia=identaic, initiator=agent, 
        unit=agent.unit, location_indicator=agent.source_structure.location_ind)
        Attachment.objects.bulk_create(
           Attachment(**{"file": attach['file'], "ddia_object": demandeAIC}) for attach in attachs
        )        
        history = DDIAHistory.objects.create(type_action=CREATE_ACTION, user=request.user, ddia_object=demandeAIC)
        return demandeAIC

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class CustomDDIARelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, DemandeNOTAM):
            serializer = DemandeNOTAMItemListSerializer(value, context=self.context)
        elif isinstance(value, DemandeSUPP):
            serializer = DemandeSUPPItemListSerializer(value, context=self.context)
        elif isinstance(value, DemandeAIC):
            serializer = DemandeAICItemListSerializer(value, context=self.context)
        return serializer.data

class ActionAgentOnDDIASerializer(serializers.ModelSerializer):
    ddia_object = CustomDDIARelatedField(read_only=True)
    class Meta:
        model = ActionAgentOnDDIA
        fields = ['ddia_object', 'prev_state', 'date_time']

class ValidationSerializer(serializers.ModelSerializer):
    ddia_object = CustomDDIARelatedField(read_only=True)
    class Meta:
        model = Validation
        fields = ['ddia_object', 'date_time']

class ApprobationSerializer(serializers.ModelSerializer):
    ddia_object = CustomDDIARelatedField(read_only=True)
    class Meta:
        model = Approbation
        fields = ['ddia_object', 'date_time']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'role', 'sex', 'function', 'quality']

class DDIAModifHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DDIAModifHistory
        fields = ['new_value', 'prev_value', 'field']

class DDIAHistorySerializer(serializers.ModelSerializer):
    modifshistory = DDIAModifHistorySerializer(read_only=True, many=True)
    # ddia_object = CustomDDIARelatedField(read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = DDIAHistory
        fields = ['user', 'type_action', 'modifshistory', 'date_time' ]


class DemandeNOTAMSerializer(serializers.ModelSerializer):
    initiator_infos = serializers.SerializerMethodField(read_only=True)
    attachments = AttachmentSerializer(read_only=True, many=True)
    unit = UnitSerializer(read_only=True)
    history = DDIAHistorySerializer(read_only=True, many=True)

    class Meta:
        model = DemandeNOTAM
        fields = '__all__'

    def get_initiator_infos(self, obj):
        user = obj.initiator.user
        return {
            'fisrtname': user.first_name,
            'lastname': user.last_name,
            'function': user.function,
            'quality': user.quality,
            'sex': user.sex
        }

class DemandeSUPPSerializer(serializers.ModelSerializer):
    initiator_infos = serializers.SerializerMethodField(read_only=True)
    attachments = AttachmentSerializer(read_only=True, many=True)
    unit = UnitSerializer(read_only=True)
    history = DDIAHistorySerializer(read_only=True, many=True)

    class Meta:
        model = DemandeSUPP
        fields = '__all__'

    def get_initiator_infos(self, obj):
        user = obj.initiator.user

        return {
            'fisrtname': user.first_name,
            'lastname': user.last_name,
            'function': user.function,
            'quality': user.quality,
            'sex': user.sex
        }


class DemandeAICSerializer(serializers.ModelSerializer):
    initiator_infos = serializers.SerializerMethodField(read_only=True)
    attachments = AttachmentSerializer(read_only=True, many=True)
    unit = UnitSerializer(read_only=True)
    history = DDIAHistorySerializer(read_only=True, many=True)

    class Meta:
        model = DemandeAIC
        fields = '__all__'

    def get_initiator_infos(self, obj):
        user = obj.initiator.user

        return {
            'fisrtname': user.first_name,
            'lastname': user.last_name,
            'function': user.function,
            'quality': user.quality,
            'sex': user.sex
        }

class LocalAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalAgent
        fields = '__all__'
    def validate(self, data):
        user = data.get('user')
        if user.role not in [LOCAL_INFORMER, LOCAL_VERIFIER]:
            raise serializers.ValidationError({"user": "A user corresponding to local agent can't have this role"})                        
        return data

class NationalAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NationalAgent
        fields = '__all__'

    def validate(self, data):
        user = data.get('user')
        if user.role is not NATIONAL_INFORMER:
            raise serializers.ValidationError({"user": "A user corresponding to national agent can't have this role"})                      
        return data

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__'
        extra_kwargs = {
            'unit': {"required": False},
            'user': {"required": True},
            'source_structure': {"required": False}
        }    

    def validate(self, data: dict):
        unit = data.get('unit')
        user = data.get('user')
        sourcestructure = data.get('source_structure')
        if user.role not in [SOURCE_AGENT, SOURCE_VERIFIER, SOURCE_STRUCTURE]:
            raise serializers.ValidationError({"user": "A user corresponding to agent can't have this role"}) 
        if unit is None and sourcestructure is None:
            raise serializers.ValidationError({"message": "You must refer at least source structure or unit"})              
        return data

    def create(self, validated_data):
        unit = validated_data.pop('unit', None)
        sourcestructure = validated_data.pop('source_structure', None)
        user = validated_data.pop('user')
        if unit is None:
            agent = Agent.objects.create(user=user, source_structure=sourcestructure)
            return agent
        agent = Agent.objects.create(user=user, unit=unit, source_structure=unit.aerodrome)
        return agent