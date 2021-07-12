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
        user_role = request.user.role
        return user_role == SOURCE_VERIFIER

    def has_object_permission(self, request, view, obj):
        agent = Agent.objects.select_related('source_structure').get(user=request.user)
        return obj.unit.aerodrome == agent.source_structure and obj.state == PENDING_VERIFICATION_STATE

class IsSourceAgent(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = request.user.role
        return user_role == SOURCE_AGENT

class IsSourceCommander(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = request.user.role
        return user_role == SOURCE_STRUCTURE

    def has_object_permission(self, request, view, obj):
        agent = Agent.objects.select_related('source_structure').get(user=request.user)
        if agent is None:
            return False
        return obj.unit.aerodrome == agent.source_structure and obj.state == PENDING_ADMISSION_STATE


class IsLocalInformer(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = request.user.role
        return user_role == LOCAL_INFORMER

    def has_object_permission(self, request, view, obj):
        localagent = LocalAgent.objects.select_related('localinformer').get(user=request.user)
        if localagent is None:
            return False
        return obj.unit.aerodrome.local_informer == localagent.localinformer and obj.state == PENDING_VALIDATION_STATE


class IsNationalInformer(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = request.user.role
        return user_role == NATIONAL_INFORMER

class CanReadDDIA(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)

class CanModifyDDIA(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)

class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = request.user.role
        return user_role == SOURCE_VERIFIER or user_role == SOURCE_AGENT
    def has_object_permission(self, request, view, obj):
        return request.user == obj.initiator.user

