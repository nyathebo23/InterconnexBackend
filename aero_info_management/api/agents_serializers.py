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
import pytz

utc=pytz.UTC



class LocalAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalAgent
        fields = '__all__'
    def validate(self, data):
        user = data.get('user')
        if user.role not in [LOCAL_INFORMER, LOCAL_VERIFIER, SOURCE_VERIFIER]:
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
            'aerodrome': {"required": False}
        }    

    def validate(self, data: dict):
        unit = data.get('unit')
        user = data.get('user')
        sourcestructure = data.get('aerodrome')
        if user.role not in [SOURCE_AGENT, SOURCE_VERIFIER, SOURCE_STRUCTURE]:
            raise serializers.ValidationError({"user": "A user corresponding to agent can't have this role"}) 
        if unit is None and sourcestructure is None:
            raise serializers.ValidationError({"message": "You must refer at least source structure or unit"})              
        return data

    def create(self, validated_data):
        unit = validated_data.pop('unit', None)
        sourcestructure = validated_data.pop('aerodrome', None)
        user = validated_data.pop('user')
        if unit is None:
            agent = Agent.objects.create(user=user, aerodrome=sourcestructure)
            return agent
        agent = Agent.objects.create(user=user, unit=unit, aerodrome=unit.aerodrome)
        return agent

class LocalAgentSerializerForHistory(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    localinformer = LocalInformerSerializerForHistory(read_only=True, many=False)
    class Meta:
        model = LocalAgent
        fields = '__all__'
    def get_aerodrome_name(self, obj):
        if obj.aerodrome is None:
            return ''
        return obj.aerodrome.name
        
class NationalAgentSerializerForHistory(serializers.ModelSerializer):
    nationalinf_name = serializers.SerializerMethodField(read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = NationalAgent
        fields = '__all__'

    def get_nationalinf_name(self, obj):
        return obj.nationalinformer.name

class AgentSerializerForHistory(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    unit = UnitSimpleSerializer(read_only=True)
    class Meta:
        model = Agent
        fields = ('id', 'user', 'unit') 


class AgentSerializerExtend(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    unit = UnitSerializer(read_only = True)
    aerodrome = AerodromeSerializer(read_only=True)
    class Meta:
        model = Agent
        fields = '__all__'


class LocalAgentSerializerExtend(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    localinformer = LocalInformerSerializerExtend(read_only=True)
    class Meta:
        model = LocalAgent
        fields = '__all__'

class NationalAgentSerializerExtend(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    nationalinformer = NationalInformerSerializer(read_only=True)
    class Meta:
        model = NationalAgent
        fields = '__all__'


class LocalAgentSerializerForHistory(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    localinformer = LocalInformerSerializerForHistory(read_only=True, many=False)
    class Meta:
        model = LocalAgent
        fields = '__all__'
    def get_aerodrome_name(self, obj):
        if obj.aerodrome is None:
            return ''
        return obj.aerodrome.name
        
class NationalAgentSerializerForHistory(serializers.ModelSerializer):
    nationalinf_name = serializers.SerializerMethodField(read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = NationalAgent
        fields = '__all__'

    def get_nationalinf_name(self, obj):
        return obj.nationalinformer.name

class AgentSerializerForHistory(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    unit = UnitSimpleSerializer(read_only=True)
    class Meta:
        model = Agent
        fields = ('id', 'user', 'unit') 

class CustomAgentRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, LocalAgent):
            serializer = LocalAgentSerializerForHistory(value)
        elif isinstance(value, NationalAgent):
            serializer = NationalAgentSerializerForHistory(value)
        elif isinstance(value, Agent):
            serializer = AgentSerializerForHistory(value)
        return serializer.data


class DDIAModifHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DDIAModifHistory
        fields = ['new_value', 'prev_value', 'field']

class DDIAHistorySerializer(serializers.ModelSerializer):
    modifshistory = DDIAModifHistorySerializer(read_only=True, many=True)
    # ddia_object = CustomDDIARelatedField(read_only=True)
    agent_object = CustomAgentRelatedField(read_only=True)
    class Meta:
        model = DDIAHistory
        fields = ['agent_object', 'type_action', 'modifshistory', 'date_time']