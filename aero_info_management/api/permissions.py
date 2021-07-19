from rest_framework import permissions
from rest_framework.decorators import permission_classes
from ..constants import *
from ..models import *


class CanInitiateDDIA(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = request.user.role
        return user_role == SOURCE_VERIFIER or user_role == SOURCE_AGENT

class IsVerifier(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        user_role = user.role
        islocalinf = request.GET.get('is_localinf') == 'yes'
        if islocalinf:
            return user_role == SOURCE_VERIFIER and LocalAgent.objects.filter(user=user).exists()
        else:
            return user_role == SOURCE_VERIFIER and Agent.objects.filter(user=user).exists()

    def has_object_permission(self, request, view, obj):
        localinf = LocalInformer.objects.filter(aerodrome=obj.unit.aerodrome).first()
        if localinf is not None:
            agent = LocalAgent.objects.filter(user=request.user, localinformer=localinf).first()
            if agent is not None:
                return obj.state == PENDING_VERIFICATION_STATE
            return False
        agent = Agent.objects.select_related('aerodrome').get(user=request.user)
        return obj.unit.aerodrome == agent.aerodrome and obj.state == PENDING_VERIFICATION_STATE

class IsSourceAgent(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = request.user.role
        return user_role == SOURCE_AGENT

class IsSourceCommander(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = request.user.role
        return user_role == SOURCE_STRUCTURE

    def has_object_permission(self, request, view, obj):
        agent = Agent.objects.select_related('aerodrome').get(user=request.user)
        if agent is None:
            return False
        return obj.unit.aerodrome == agent.aerodrome and obj.state == PENDING_ADMISSION_STATE

class IsAuthorityLocalInformer(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = request.user.role
        return user_role == LOCAL_INFORMER

    def has_object_permission(self, request, view, obj):
        localinf = LocalInformer.objects.filter(aerodrome=None)
        localagent = LocalAgent.objects.filter(user=request.user, localinformer__in=localinf).first()
        if localagent is None:
            return False
        return obj.state == PENDING_VALIDATION_STATE

class IsNationalInformer(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = request.user.role
        return user_role == NATIONAL_INFORMER

class CanReadDDIA(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user 
        if user.role == SOURCE_AGENT:
            agent = Agent.objects.select_related('unit').get(user=user)
            return obj.unit == agent.unit
        elif user.role == SOURCE_VERIFIER:
            agent = Agent.objects.select_related('aerodrome').filter(user=user).first()
            if agent is None:
                localagent = LocalAgent.objects.select_related('localinformer__aerodrome').get(user=user)
                return localagent.localinformer.aerodrome == obj.unit.aerodrome and obj.state != DRAFT_STATE 
            return agent.aerodrome == obj.unit.aerodrome and obj.state != DRAFT_STATE
        elif user.role == SOURCE_STRUCTURE:
            agent = Agent.objects.select_related('aerodrome').get(user=user)
            return agent.aerodrome == obj.unit.aerodrome and obj.state not in [DRAFT_STATE, PENDING_VERIFICATION_STATE]
        elif user.role == LOCAL_INFORMER or user.role == LOCAL_VERIFIER:
            agent = LocalAgent.objects.select_related('localinformer').get(user=user) 
            return  obj.state not in [DRAFT_STATE, PENDING_VERIFICATION_STATE, PENDING_ADMISSION_STATE]
        elif user.role == NATIONAL_INFORMER:
            return  obj.state not in [DRAFT_STATE, PENDING_VERIFICATION_STATE, PENDING_ADMISSION_STATE]
        return super().has_object_permission(request, view, obj)

class CanModifyDDIA(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)

class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = request.user.role
        return user_role == SOURCE_VERIFIER or user_role == SOURCE_AGENT
    def has_object_permission(self, request, view, obj):
        return request.user == obj.initiator

