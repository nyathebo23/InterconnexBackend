from django.contrib.auth import get_user_model
from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db.models.base import Model
from django.db.models.deletion import DO_NOTHING
from django.db.models.fields.json import DataContains
from .constants import *
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

class RequestReferral(models.Model):
    message = models.TextField()
    agent_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING, related_name='reqs_referral_agent')
    agent_id = models.PositiveBigIntegerField()
    agent_object = GenericForeignKey('agent_type', 'agent_id')       
    ddia_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='reqs_referral_ddia')
    id_object = models.PositiveBigIntegerField()
    ddia_object = GenericForeignKey('ddia_type', 'id_object')
    date_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['date_time']

class DDIAHistory(models.Model):
    agent_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING, related_name='history_agent')
    agent_id = models.PositiveBigIntegerField()
    agent_object = GenericForeignKey('agent_type', 'agent_id')    
    # user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    type_action = models.CharField(max_length=20, choices=TYPES_ACTION)
    ddia_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='history_ddia')
    id_object = models.PositiveBigIntegerField()
    ddia_object = GenericForeignKey('ddia_type', 'id_object')
    date_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['date_time']

class DDIAModifHistory(models.Model):
    history = models.ForeignKey(DDIAHistory, on_delete=models.CASCADE, related_name='modifshistory')
    new_value = models.TextField()
    prev_value = models.TextField()
    field = models.CharField(max_length=50)

class Notification(models.Model):
    receiver_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    receiver_id = models.PositiveBigIntegerField()
    receiver_object = GenericForeignKey('receiver_type', 'receiver_id')    
    event = models.CharField(max_length=20)
    ddia_type = models.CharField(max_length=20, choices=TYPES_DDIA)
    ref_ddia = models.CharField(max_length=20)   
    new_ddia_state = models.CharField(max_length=50, choices=STATES)
    read = models.BooleanField(default=False)
    date_time = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-date_time']


class Aerodrome(models.Model):
    name = models.CharField(max_length=80, unique=True)
    location_ind = models.CharField(max_length=10, unique=True)
    is_conceded = models.BooleanField(default=False)
    notifications = GenericRelation(Notification, related_query_name='aerodrome', content_type_field='receiver_type', object_id_field='receiver_id')
    def __str__(self) -> str:
        return self.name

class Unit(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=70)
    phone_number = models.CharField(max_length=20, unique=True)
    fax = models.CharField(max_length=40)
    address = models.CharField(max_length=80)
    rsfta = models.CharField(max_length=100, blank=True)
    aerodrome = models.ForeignKey(Aerodrome, on_delete=models.CASCADE, related_name='units')
    notifications = GenericRelation(Notification, related_query_name='unit', content_type_field='receiver_type', object_id_field='receiver_id')
    def __str__(self) -> str:
        return self.name + " "+ self.aerodrome.name

class LocalInformer(models.Model):
    name = models.CharField(max_length=50)
    aerodrome = models.ForeignKey(Aerodrome, on_delete=models.CASCADE, blank=True, null=True, related_name='localinformer')
    unit = models.OneToOneField(Unit, on_delete=models.SET_NULL, blank=True, null=True)
    notifications = GenericRelation(Notification, related_query_name='localinformer', content_type_field='receiver_type', object_id_field='receiver_id')

    def __str__(self) -> str:
        return self.name

class NationalInformer(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(default='segc@ccaa.aero')
    is_authority = models.BooleanField(default=False)
    notifications = GenericRelation(Notification, related_query_name='nationalinformer', content_type_field='receiver_type', object_id_field='receiver_id')
    def __str__(self) -> str:
        return self.name

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)
    aerodrome = models.ForeignKey(Aerodrome, on_delete=models.SET_NULL, blank=True, null=True)
    history = GenericRelation(DDIAHistory, related_query_name='agent', content_type_field='agent_type', object_id_field='agent_id')
    requests_referral = GenericRelation(RequestReferral, related_query_name='agent', content_type_field='agent_type', object_id_field='agent_id')
    def __str__(self) -> str:
        return self.user.username+ ' - '+ self.user.role

class LocalAgent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    localinformer = models.ForeignKey(LocalInformer, on_delete=models.DO_NOTHING)
    history = GenericRelation(DDIAHistory, related_query_name='local_agent', content_type_field='agent_type', object_id_field='agent_id')
    requests_referral = GenericRelation(RequestReferral, related_query_name='local_agent', content_type_field='agent_type', object_id_field='agent_id')
    def __str__(self) -> str:
        return self.user.username+ ' - '+ self.user.role

class NationalAgent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nationalinformer = models.ForeignKey(NationalInformer, on_delete=models.DO_NOTHING)
    history = GenericRelation(DDIAHistory, related_query_name='national_agent', content_type_field='agent_type', object_id_field='agent_id')
    requests_referral = GenericRelation(RequestReferral, related_query_name='national_agent', content_type_field='agent_type', object_id_field='agent_id')
    def __str__(self) -> str:
        return self.user.username+ ' - '+ self.user.role
    
class DDIA(models.Model):
    initiator = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    ident_ddia = models.CharField(unique=True, max_length=20, blank=True)
    state = models.CharField(max_length=70, choices=STATES, default=DRAFT_STATE)
    deposit_datetime = models.DateTimeField(auto_now_add=True)
    unit = models.ForeignKey(Unit, on_delete=models.DO_NOTHING)
    location_indicator = models.CharField(max_length=10)
    publication_code = models.CharField(max_length=70, blank=True)
    class Meta:
        ordering = ['deposit_datetime']
        abstract = True


class Attachment(models.Model):
    ddia_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='attachments')
    object_id = models.PositiveBigIntegerField()
    ddia_object = GenericForeignKey('ddia_type', 'object_id')
    # pathname = models.FilePathField()
    file = models.FileField()

class NationalInformerAction(models.Model):
    national_agent = models.ForeignKey(NationalAgent, on_delete=models.CASCADE, related_name='national_inf_actions')
    ddia_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    ddia_object = GenericForeignKey('ddia_type', 'object_id')
    new_state = models.CharField(max_length=40, choices=STATES_AFTER_NATIONALINF_ACTION)
    date_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together   = ('ddia_type', 'object_id', 'new_state')
        ordering = ['date_time']

class LocalInformerAction(models.Model):
    local_agent = models.ForeignKey(LocalAgent, on_delete=models.CASCADE, related_name='local_inf_actions')
    ddia_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    ddia_object = GenericForeignKey('ddia_type', 'object_id')
    prev_state = models.CharField(max_length=40, choices=((PENDING_VERIFICATION_STATE, PENDING_VERIFICATION_STATE), (PENDING_VALIDATION_STATE, PENDING_VALIDATION_STATE)))
    new_state = models.CharField(max_length=40, choices=((PENDING_ADMISSION_STATE, PENDING_ADMISSION_STATE), (PENDING_APPROVAL_STATE, PENDING_APPROVAL_STATE)))
    target_nationalinf = models.ForeignKey(NationalInformer, on_delete=models.SET_NULL, blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=True)   
    class Meta:
        unique_together   = ('ddia_type', 'object_id', 'prev_state') 
        ordering = ['date_time']

class SourceStructureAction(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='actionsonddia')
    ddia_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    ddia_object = GenericForeignKey('ddia_type', 'object_id')
    prev_state = models.CharField(max_length=40, choices=PREVSTATES_FOR_AERODROME_AGENT)
    new_state = models.CharField(max_length=40, choices=NEXTSTATES_FOR_AERODROME_AGENT)
    date_time = models.DateTimeField(auto_now_add=True) 
    class Meta:
        unique_together = ('ddia_type', 'object_id', 'prev_state')
        ordering = ['date_time']

class DemandeNOTAM(DDIA):
    range_action = models.CharField(max_length=120, blank=True)
    type_notam = models.CharField(max_length=10, choices=TYPES_NOTAM, default=NOTAMN)
    coords = models.CharField(max_length=120, blank=True)
    validity_period_type = models.CharField(max_length=15, choices=PERIOD_TYPES, default=PLANNED)
    code_notam_replaceorcancel = models.CharField(max_length=80, null=True, blank=True)
    start_val_period = models.DateTimeField()
    end_val_period = models.DateTimeField()
    daily_freq_start = models.TimeField(blank=True, null=True)
    daily_freq_end = models.TimeField(blank=True, null=True)
    daily_freq_type = models.CharField(max_length=30, choices=PERIOD_TYPES, default=PLANNED)
    lower_vertical_limit = models.CharField(max_length=50, blank=True)
    upper_vertical_limit = models.CharField(max_length=50, blank=True)
    descriptive_text = models.TextField(blank=True)
    attachments = GenericRelation(Attachment, related_query_name='notam', content_type_field='ddia_type')
    national_inf_actions = GenericRelation(NationalInformerAction, related_query_name='notam', content_type_field='ddia_type')
    local_inf_actions = GenericRelation(LocalInformerAction, related_query_name='notam', content_type_field='ddia_type')
    sourcestruct_actions = GenericRelation(SourceStructureAction, related_query_name='notam',  content_type_field='ddia_type')
    referral = GenericRelation(RequestReferral, related_query_name='notam',  content_type_field='ddia_type', object_id_field='id_object')
    history = GenericRelation(DDIAHistory, related_query_name='notam', content_type_field='ddia_type', object_id_field='id_object')


class DemandeSUPP(DDIA):
    type_suppaip = models.CharField(max_length=15, choices=TYPES_SUPPAIP, default=SUPPAIPN)
    object = models.TextField()
    code_ddia_replaced = models.CharField(max_length=80, null=True, blank=True)
    aip_target_sections = models.TextField()
    start_val_period = models.DateTimeField()
    end_val_period = models.DateTimeField()      
    descriptive_text = models.TextField(blank=True)
    attachments = GenericRelation(Attachment, related_query_name='suppaip', content_type_field='ddia_type')
    national_inf_actions = GenericRelation(NationalInformerAction, related_query_name='suppaip', content_type_field='ddia_type')
    local_inf_actions = GenericRelation(LocalInformerAction, related_query_name='suppaip', content_type_field='ddia_type')
    sourcestruct_actions = GenericRelation(SourceStructureAction, related_query_name='suppaip',  content_type_field='ddia_type')
    referral = GenericRelation(RequestReferral, related_query_name='suppaip',  content_type_field='ddia_type', object_id_field='id_object')
    history = GenericRelation(DDIAHistory, related_query_name='suppaip', content_type_field='ddia_type', object_id_field='id_object')

class DemandeAIC(DDIA):
    subject = models.CharField(max_length=50, choices=AIC_SUBJECTS)
    object = models.TextField()
    descriptive_text = models.TextField(blank=True)
    attachments = GenericRelation(Attachment, related_query_name='aic', content_type_field='ddia_type')
    national_inf_actions = GenericRelation(NationalInformerAction, related_query_name='aic', content_type_field='ddia_type')
    local_inf_actions = GenericRelation(LocalInformerAction, related_query_name='aic', content_type_field='ddia_type')
    sourcestruct_actions = GenericRelation(SourceStructureAction, related_query_name='aic',  content_type_field='ddia_type')
    referral = GenericRelation(RequestReferral, related_query_name='aic',  content_type_field='ddia_type', object_id_field='id_object')
    history = GenericRelation(DDIAHistory, related_query_name='aic', content_type_field='ddia_type', object_id_field='id_object')




