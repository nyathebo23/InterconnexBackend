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
        extra_kwargs = {
            "aerodrome": {
                "required": False,
            }
        }

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

    def validate(self, data: dict):
        is_authority = data.get('is_authority')
        if is_authority == True:
            nationalInfExist = NationalInformer.objects.filter(is_authority=True).exists()
            if nationalInfExist:
                raise serializers.ValidationError({'is_authority': 'the national informant with is_authority = True must be unique'})
        name = data.get('name')
        nationalInfExist = NationalInformer.objects.filter(name=name).exists()
        if nationalInfExist:
            raise serializers.ValidationError({'name': 'The name of the national informant must be unique'})
        return data

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


class LocalInformerSerializerExtend(serializers.ModelSerializer):
    unit = UnitWithoutAerodromeSerializer(read_only=True)
    aerodrome = AerodromeSerializer(read_only=True)
    class Meta:
        model = LocalInformer
        fields = '__all__'
    
class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['file']

# class LocalInformerSerializerForHistory(serializers.ModelSerializer):
#     aerodrome_name = serializers.SerializerMethodField(read_only=True)
#     class Meta:
#         model = LocalInformer
#         fields = ['name', 'aerodrome_name']
    
#     def get_aerodrome_name(self, obj):
#         if obj.aerodrome is None:
#             return ''
#         return obj.aerodrome.name

class DemandeNOTAMItemListSerializer(serializers.HyperlinkedModelSerializer):
    unit_name = serializers.SerializerMethodField(read_only=True)
    airport_name = serializers.SerializerMethodField(read_only=True)
    type_ddia = serializers.SerializerMethodField(read_only=True) 
    class Meta:
        model = DemandeNOTAM
        fields = [
            'id',
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
            'id',
            'type_ddia',
            'unit_name', 
            'airport_name', 
            'url', 
            'type_suppaip', 
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

    def get_type_ddia(self, obj):
        return 'SUPP AIP'

class DemandeAICItemListSerializer(serializers.HyperlinkedModelSerializer):
    unit_name = serializers.SerializerMethodField(read_only=True)
    airport_name = serializers.SerializerMethodField(read_only=True)   
    type_ddia = serializers.SerializerMethodField(read_only=True) 
    class Meta:
        model = DemandeAIC
        fields = [
            'id',
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

class CustomStructureFieldForNotification(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, Unit):
            serializer = UnitSimpleSerializer(value)
        elif isinstance(value, Aerodrome):
            serializer = AerodromeSerializer(value)
        elif isinstance(value, LocalInformer):
            serializer = LocalInformerSerializer(value)
        elif isinstance(value, NationalInformer):
            serializer = NationalInformerSerializer(value)
        return serializer.data

class NotificationSerializer(serializers.ModelSerializer):
    receiver_object = CustomStructureFieldForNotification(read_only=True)
    class Meta:
        model = Notification
        exclude = ['receiver_id', 'receiver_type']

class SourceStructureActionSerializer(serializers.ModelSerializer):
    ddia_object = CustomDDIARelatedField(read_only=True)
    class Meta:
        model = SourceStructureAction
        fields = ['ddia_object', 'prev_state', 'date_time', 'new_state']

class LocalInformerActionSerializer(serializers.ModelSerializer):
    target_nationalinf = NationalInformerSerializer(read_only=True)
    ddia_object = CustomDDIARelatedField(read_only=True)
    class Meta:
        model = LocalInformerAction
        fields = ['ddia_object', 'date_time', 'prev_state', 'new_state', 'target_nationalinf']

class NationalInformerActionSerializer(serializers.ModelSerializer):
    ddia_object = CustomDDIARelatedField(read_only=True)
    class Meta:
        model = NationalInformerAction
        fields = ['ddia_object', 'date_time', 'new_state']


class AerodromeExtendSerializer(serializers.ModelSerializer):
    localinformer = LocalInformerSerializer(read_only=True)
    units = UnitReducedSerializer(read_only=True, many=True)
    class Meta:
        model = Aerodrome
        exclude = ['location_ind']

