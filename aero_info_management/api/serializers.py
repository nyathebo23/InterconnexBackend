from inspect import indentsize
from os import read
from django.contrib.contenttypes import fields
from rest_framework import request, serializers
from ..models import *
from ..constants import *
from django.db.models import Q
from datetime import datetime, date, tzinfo
from django.contrib.auth import get_user_model
import pytz

utc=pytz.UTC

User = get_user_model()

notam_type = ContentType.objects.get_for_model(DemandeNOTAM)
suppaip_type = ContentType.objects.get_for_model(DemandeSUPP)
aic_type = ContentType.objects.get_for_model(DemandeAIC)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email' ,'first_name', 'last_name', 'sex', 'role', 'function', 'quality', 'is_staff']

class LocalInformerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalInformer
        fields = '__all__'

    def validate(self, data: dict):
        if data.get('name') is None and data.get('unit') is None:
            raise serializers.ValidationError({"name": "You must refer name of local informer if it isn't inside aerodrome"})
        if data.get('unit') is None and data.get('aerodrome') is not None:
            raise serializers.ValidationError({"unit": "You must refer unit which is local informer"})
        return data

    def create(self, validated_data: dict):
        unit = validated_data.pop('unit', None)
        name = validated_data.pop("name")
        if unit is None:
            localinf = LocalInformer.objects.create(name=name)
            return localinf
        if name is None:
            name = unit.name
        localinf = LocalInformer.objects.create(name=name, unit=unit, aerodrome=unit.aerodrome)
        return localinf

class NationalInformerSerializer(serializers.ModelSerializer):
    class Meta:
        model = NationalInformer
        fields = '__all__'

class AerodromeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aerodrome
        fields = '__all__'

class UnitSerializer(serializers.ModelSerializer):
    aerodrome_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Unit
        fields = '__all__'

    def get_aerodrome_name(self, obj):
        return obj.aerodrome.name

class UnitWithoutAerodromeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        exclude = ['aerodrome']

class UnitSimpleSerializer(serializers.ModelSerializer):
    aerodrome_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Unit
        fields = ['name', 'aerodrome_name']

    def get_aerodrome_name(self, obj):
        if obj.aerodrome is None:
            return ''
        return obj.aerodrome.name


class UnitReducedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name']

class AerodromeExtendSerializer(serializers.ModelSerializer):
    units = UnitReducedSerializer(many=True, read_only=True)
    localinformer = LocalInformerSerializer(read_only=True)
    class Meta:
        model = Aerodrome
        fields = ['id', 'name', 'units', 'localinformer']

class LocalInformerSerializerExtend(serializers.ModelSerializer):
    unit = UnitSerializer(read_only=True)
    aerodrome = AerodromeSerializer(read_only=True)
    class Meta:
        model = LocalInformer
        fields = '__all__'
    
class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file']

class LocalInformerSerializerForHistory(serializers.ModelSerializer):
    aerodrome_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = LocalInformer
        fields = ['name', 'aerodrome_name']
    
    def get_aerodrome_name(self, obj):
        if obj.aerodrome is None:
            return ''
        return obj.aerodrome.name






