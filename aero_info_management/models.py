from django.contrib.auth import get_user_model
from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import DO_NOTHING
from django.db.models.fields.json import DataContains
from .constants import *
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

# Create your models here.
# class CustomUser(AbstractUser):
#     sex = models.CharField(max_length=10, choices=SEX_CHOICES)
#     function = models.CharField(max_length=40, blank=True)
#     quality = models.CharField(max_length=40, blank=True)
#     role = models.CharField(max_length=40, choices=USERS_ROLES)
#     linked_agent_class = models.CharField(max_length=15)

class RequestReferral(models.Model):
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    ddia_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    id_object = models.PositiveBigIntegerField()
    ddia_object = GenericForeignKey('ddia_type', 'id_object')
    date_time = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ['date_time']

class DDIAHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    type_action = models.CharField(max_length=20, choices=TYPES_ACTION)
    ddia_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
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

class LocalInformer(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self) -> str:
        return self.name

class NationalInformer(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self) -> str:
        return self.name

class Aerodrome(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=80, unique=True)
    location_ind = models.CharField(max_length=10, unique=True)
    local_informer = models.ForeignKey(LocalInformer, on_delete=DO_NOTHING)
    def __str__(self) -> str:
        return self.name

class Unit(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=70)
    phone_number = models.CharField(max_length=20, unique=True)
    fax = models.CharField(max_length=40)
    address = models.CharField(max_length=80)
    rsfta = models.CharField(max_length=100, blank=True)
    aerodrome = models.ForeignKey(Aerodrome, on_delete=models.CASCADE)
    def __str__(self) -> str:
        return self.name + " "+ self.aerodrome.name

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.DO_NOTHING, blank=True, null=True)
    source_structure = models.ForeignKey(Aerodrome, on_delete=models.DO_NOTHING, blank=True)
    def __str__(self) -> str:
        return self.user.username+ ' - '+ self.user.role
    def get_completed_name(self):
        return self.user.last_name + ' ' + self.user.first_name

class LocalAgent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    localinformer = models.ForeignKey(LocalInformer, on_delete=models.DO_NOTHING)
    def get_completed_name(self):
        return self.user.last_name + ' ' + self.user.first_name

class NationalAgent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nationalinformer = models.ForeignKey(NationalInformer, on_delete=models.DO_NOTHING)
    def get_completed_name(self):
        return self.user.last_name + ' ' + self.user.first_name

class DDIA(models.Model):
    initiator = models.ForeignKey(Agent, on_delete=models.DO_NOTHING)
    ident_ddia = models.CharField(unique=True, max_length=20, blank=True)
    state = models.CharField(max_length=70, choices=STATES, default=DRAFT_STATE)
    deposit_datetime = models.DateTimeField(default=datetime.now())
    unit = models.ForeignKey(Unit, on_delete=models.DO_NOTHING)
    location_indicator = models.CharField(max_length=10)
    publication_code = models.CharField(max_length=70, blank=True)
    class Meta:
        abstract = True

class Attachment(models.Model):
    ddia_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='attachments')
    object_id = models.PositiveBigIntegerField()
    ddia_object = GenericForeignKey('ddia_type', 'object_id')
    # pathname = models.FilePathField()
    file = models.FileField()

class Approbation(models.Model):
    national_agent = models.ForeignKey(NationalAgent, on_delete=models.CASCADE,related_name='approbations')
    ddia_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    ddia_object = GenericForeignKey('ddia_type', 'object_id')
    new_state = models.CharField(max_length=40, choices=STATES_AFTER_VALIDATION)
    date_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together   = ('ddia_type', 'object_id')
        ordering = ['date_time']

class Validation(models.Model):
    local_agent = models.ForeignKey(LocalAgent, on_delete=models.CASCADE, related_name='validations')
    ddia_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    ddia_object = GenericForeignKey('ddia_type', 'object_id')
    new_state = models.CharField(max_length=40, choices=STATES_AFTER_APPROBATION)
    date_time = models.DateTimeField(auto_now_add=True)   
    class Meta:
        unique_together   = ('ddia_type', 'object_id') 
        ordering = ['date_time']

class ActionAgentOnDDIA(models.Model):
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
    range_action = models.CharField(max_length=80, blank=True)
    type_notam = models.CharField(max_length=10, choices=TYPES_NOTAM, default=NOTAMN)
    coords = models.CharField(max_length=50, blank=True)
    periode_type_notam = models.CharField(max_length=15, choices=PERIOD_TYPES, default=PLANNED)
    start_val_period = models.DateField()
    end_val_period = models.DateField()
    daily_freq_start = models.TimeField()
    daily_freq_end = models.TimeField()
    lower_limit = models.CharField(max_length=50, blank=True)
    upper_limit = models.CharField(max_length=50, blank=True)
    descriptive_text = models.TextField(blank=True)
    attachments = GenericRelation(Attachment, related_query_name='notam', content_type_field='ddia_type')
    approbations = GenericRelation(Approbation, related_query_name='notam', content_type_field='ddia_type')
    validations = GenericRelation(Validation, related_query_name='notam', content_type_field='ddia_type')
    agentactions = GenericRelation(ActionAgentOnDDIA, related_query_name='notam',  content_type_field='ddia_type')
    history = GenericRelation(DDIAHistory, related_query_name='notam', content_type_field='ddia_type', object_id_field='id_object')

        

class DemandeSUPP(DDIA):
    type_suppaip = models.CharField(max_length=15, choices=TYPES_SUPPAIP, default=SUPPAIPN)
    object = models.TextField()
    target_section = models.CharField(max_length=80, blank=True)
    start_val_period = models.DateField()
    end_val_period = models.DateField()      
    descriptive_text = models.TextField(blank=True)
    attachments = GenericRelation(Attachment, related_query_name='notam', content_type_field='ddia_type')
    approbations = GenericRelation(Approbation, related_query_name='suppaip', content_type_field='ddia_type')
    validations = GenericRelation(Validation, related_query_name='suppaip', content_type_field='ddia_type')
    agentactions = GenericRelation(ActionAgentOnDDIA, related_query_name='suppaip',  content_type_field='ddia_type')
    history = GenericRelation(DDIAHistory, related_query_name='suppaip', content_type_field='ddia_type', object_id_field='id_object')


class DemandeAIC(DDIA):
    subject = models.TextField()
    object = models.TextField()
    descriptive_text = models.TextField(blank=True)
    attachments = GenericRelation(Attachment, related_query_name='notam', content_type_field='ddia_type')
    approbations = GenericRelation(Approbation, related_query_name='aic', content_type_field='ddia_type')
    validations = GenericRelation(Validation, related_query_name='aic', content_type_field='ddia_type')
    agentactions = GenericRelation(ActionAgentOnDDIA, related_query_name='aic',  content_type_field='ddia_type')
    history = GenericRelation(DDIAHistory, related_query_name='aic', content_type_field='ddia_type', object_id_field='id_object')
