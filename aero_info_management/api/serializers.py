from django.contrib.contenttypes import fields
from rest_framework import request, serializers
from ..models import *
from ..constants import *
from django.db.models import Q

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
        exclude = ['ddia_type', 'ddia_id', 'ddia_object']

class DemandeNOTAMSerializer(serializers.ModelSerializer):
    # initiator = serializers.CharField(source='get_completed_name', read_only=True)
    attachments = AttachmentSerializer(read_only=True, many=True)
    class Meta:
        model = DemandeNOTAM
        fields = '__all__'

class DemandeSUPPSerializer(serializers.ModelSerializer):
    # initiator = serializers.CharField(source='get_completed_name', read_only=True)
    attachments = AttachmentSerializer(read_only=True, many=True)
    class Meta:
        model = DemandeSUPP
        fields = '__all__'

class DemandeAICSerializer(serializers.ModelSerializer):
    # initiator = serializers.CharField(source='get_completed_name', read_only=True)
    attachments = AttachmentSerializer(read_only=True, many=True)
    class Meta:
        model = DemandeAIC
        fields = '__all__'

class DemandeNOTAMForCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeNOTAM
        exclude = ['initiator', 'unit', 'location_indicator']

    def create(self, validated_data):
        request = self.context.get("request")
        agent = Agent.objects.get(user=request.user)
        # attachs = validated_data.pop("attachments")
        demandeNOTAM = DemandeNOTAM.objects.create(**validated_data, initiator=agent, unit=agent.unit, location_indicator=agent.source_structure.location_ind)
        # Attachment.objects.bulk_create(
        #     {"file": attach['file'], "ddia_object": demandeNOTAM} for attach in attachs
        # )
        history = DDIAHistory.objects.create(type_action=CREATE_ACTION, user=request.user, ddia_object=demandeNOTAM)
        return demandeNOTAM

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class DemandeSUPPForCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeSUPP
        exclude = ['initiator', 'unit', 'location_indicator']

    def create(self, validated_data):
        request = self.context.get("request")
        agent = Agent.objects.get(user=request.user)
        # attachs = validated_data.pop("attachments")
        demandeSUPP = DemandeSUPP.objects.create(**validated_data, initiator=agent, unit=agent.unit, location_indicator=agent.source_structure.location_ind)
        # Attachment.objects.bulk_create(
        #     {"file": attach['file'], "ddia_object": demandeSUPP} for attach in attachs
        # )        
        history = DDIAHistory.objects.create(type_action=CREATE_ACTION, user=request.user, ddia_object=demandeSUPP)
        return demandeSUPP

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class DemandeAICForCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeAIC
        exclude = ['initiator', 'unit', 'location_indicator']

    def create(self, validated_data):
        request = self.context.get("request")
        agent = Agent.objects.get(user=request.user)
        # attachs = validated_data.pop("attachments")
        demandeAIC = DemandeAIC.objects.create(**validated_data, initiator=agent, unit=agent.unit, location_indicator=agent.source_structure.location_ind)
        # Attachment.objects.bulk_create(
        #     {"file": attach['file'], "ddia_object": demandeAIC} for attach in attachs
        # )        
        history = DDIAHistory.objects.create(type_action=CREATE_ACTION, user=request.user, ddia_object=demandeAIC)
        return demandeAIC

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class CustomDDIARelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, DemandeNOTAM):
            serializer = DemandeNOTAMSerializer(value)
        elif isinstance(value, DemandeSUPP):
            serializer = DemandeSUPPSerializer(value)
        elif isinstance(value, DemandeAIC):
            serializer = DemandeAICSerializer(value)
        return serializer.data

class ActionAgentOnDDIASerializer(serializers.ModelSerializer):
    ddia_object = CustomDDIARelatedField(read_only=True)
    agent = serializers.CharField(source='get_completed_name', read_only=True)
    class Meta:
        model = ActionAgentOnDDIA
        exclude = ['new_state', 'object_id', 'ddia_type']

class ValidationSerializer(serializers.ModelSerializer):
    ddia_object = CustomDDIARelatedField(read_only=True)
    agent = serializers.CharField(source='get_completed_name', read_only=True)
    class Meta:
        model = Validation
        exclude = ['new_state', 'object_id', 'ddia_type']

class ApprobationSerializer(serializers.ModelSerializer):
    ddia_object = CustomDDIARelatedField(read_only=True)
    agent = serializers.CharField(source='get_completed_name', read_only=True)
    class Meta:
        model = Approbation
        exclude = ['new_state', 'object_id', 'ddia_type']    

class LocalAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalAgent
        fields = '__all__'

    def validate(self, data):
        user = data.get('user')
        # user = User.objects.filter(id=user_id)
        # if not user.exists():
        #     raise serializers.ValidationError({"user": "The User that you referred does not exists"})    
        # user = user.first()
        if user.role not in [LOCAL_INFORMER, LOCAL_VERIFIER]:
            raise serializers.ValidationError({"user": "A user corresponding to local agent can't have this role"})         
        localinf = data.get('localinformer')
        # localinf = LocalInformer.objects.filter(id=localinf_id)
        # if not localinf.exists():
        #     raise serializers.ValidationError({"localinformer": "The Local informer that you referred does not exists"})                
        return data

class NationalAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NationalAgent
        fields = '__all__'

    def validate(self, data):
        user = data.get('user')
        # user = User.objects.filter(id=user_id)
        # if not user.exists():
        #     raise serializers.ValidationError({"user": "The User that you referred does not exists"})    
        # user = user.first()
        if user.role is not NATIONAL_INFORMER:
            raise serializers.ValidationError({"user": "A user corresponding to national agent can't have this role"})         
        # nationalinf = data.get('localinformer')
        # nationalinf = LocalInformer.objects.filter(id=nationalinf_id)
        # if not nationalinf.exists():
        #     raise serializers.ValidationError({"nationalinformer": "The National informer that you referred does not exists"})                
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
        # user = User.objects.filter(id=user_id)
        # if not user.exists():
        #     raise serializers.ValidationError({"user": "The User that you referred does not exists"})
        # user = user.first()
        if user.role not in [SOURCE_AGENT, SOURCE_VERIFIER, SOURCE_STRUCTURE]:
            raise serializers.ValidationError({"user": "A user corresponding to agent can't have this role"}) 
        if unit is None:
            if sourcestructure is None:
                raise serializers.ValidationError({"message": "You must refer at least source structure or unit"})              
            # sourcestructure = Aerodrome.objects.filter(id=sourcestructure_id)
            # if not sourcestructure.exists():
            #     raise serializers.ValidationError({"source_structure": "The Source structure that you referred does not exists"})                
        # if sourcestructure_id is None:
        #     unit = Unit.objects.filter(id=unit_id)
        #     if not unit.exists():
        #         raise serializers.ValidationError({"unit": "The Unit that you referred does not exists"})
               
        return data

    def create(self, validated_data):
        unit = validated_data.pop('unit', None)
        sourcestructure = validated_data.pop('source_structure', None)
        user = validated_data.pop('user')
        if unit is None:
            # sourcestructure = Aerodrome.objects.get(id=sourcestructure_id)
            agent = Agent.objects.create(user=user, source_structure=sourcestructure)
            return agent
        # unit = Unit.objects.get(id=unit_id)
        agent = Agent.objects.create(user=user, unit=unit, source_structure=unit.aerodrome)
        return agent