from .stats_views import *
from django.db import router
from django.urls import path, include
from .views import *
from .ddia_viewsets import *
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

aic_create = DemandeAICViewSet.as_view({'post': 'create'})
notam_create = DemandeNOTAMViewSet.as_view({'post': 'create'})
suppaip_create = DemandeSUPPViewSet.as_view({'post': 'create'})
aic_update = DemandeAICViewSet.as_view({'put': 'update'})
notam_update = DemandeNOTAMViewSet.as_view({'put': 'update'})
suppaip_update = DemandeSUPPViewSet.as_view({'put': 'update'})
aic_retrieve = DemandeAICViewSet.as_view({'get': 'retrieve'})
notam_retrieve = DemandeNOTAMViewSet.as_view({'get': 'retrieve'})
suppaip_retrieve = DemandeSUPPViewSet.as_view({'get': 'retrieve'})
ddia_submittoverif = DDIAControlViewset.as_view({'post': 'submittoverif'})
ddia_verify = DDIAControlViewset.as_view({'post': 'verify'})
ddia_admit = DDIAControlViewset.as_view({'post': 'admit'})
ddia_validate = DDIAControlViewset.as_view({'post': 'validate'})
ddia_approve = DDIAControlViewset.as_view({'post': 'approve'})
ddia_cancel = DDIAControlViewset.as_view({'post': 'cancel'})
ddia_publish = DDIAControlViewset.as_view({'post': 'set_published'})
router.register(r'agent', AgentViewSet, basename='agent')
router.register(r'local-agent', LocalAgentViewSet, basename='localagent')
router.register(r'national-agent', NationalAgentViewSet, basename='nationalagent')

router.register(r'units', UnitViewSet)
router.register(r'aerodromes', AerodromeViewSet)
router.register(r'local-informers', LocalInformerViewSet),
router.register(r'national-informers', NationalInformerViewSet)
urlpatterns = [
    # path('source/listDDIA/<str:type_ddia>', )
    path('delete-user/<int:pk>', delete_user, name='deleteuser'),
    path('agent-infos/', get_agent_infos, name='agent-infos'),
    path('nationalinf-ddia-target/<str:type_ddia>/<int:id>', get_target_nationalinformer, name='nationalinf-ddia-target'),
    path('localagent-infos/', get_localagent_infos, name='localagent-infos'),
    path('nationalagent-infos/', get_nationalagent_infos, name='nationalagent-infos'),
    path('demande-aic/create/', aic_create, name='aic-create'),
    path('demande-notam/create/', notam_create, name='notam-create'),
    path('demande-suppaip/create/', suppaip_create, name='supp-create'),
    path('demande-aic/update/<int:pk>/', aic_update, name='aic-update'),
    path('demande-notam/update/<int:pk>/', notam_update, name='notam-update'),
    path('demande-suppaip/update/<int:pk>/', notam_update, name='supp-update'),
    path('demande-aic/<int:pk>', aic_retrieve, name='demandeaic-detail'),
    path('demande-notam/<int:pk>', notam_retrieve, name='demandenotam-detail'),
    path('demande-suppaip/<int:pk>', suppaip_retrieve, name='demandesupp-detail'),
    
    path('notifications/source/', get_notifications_sourceunit, name='ddia-unit-notifs'),
    path('notifications/sourceverfier/', get_notifications_sourceverifier, name='ddia-unitverif-notifs'),
    path('notifications/sourcestructure/', get_notifications_sourcecommand, name='ddia-aerodrome-notifs'),
    path('notifications/localinformer/', get_notifications_localinformer, name='ddia-localinf-notifs'),
    path('notifications/nationalinformer/', get_notifications_nationalinformer, name='ddia-nationalinf-notifs'),
    path('notifications/set-as-read/<int:idNotif>/', mark_notif_as_read, name='set-read-notifs'),

    path('submittoverif/<str:type_ddia>/<int:pk>', ddia_submittoverif, name='ddia-submittoverify'),
    path('cancel/<str:type_ddia>/<int:pk>', ddia_cancel, name='ddia-cancel'),
    path('code-publish/<str:type_ddia>/<int:pk>', ddia_publish, name='ddia-codepublish-set'),
    path('verify/<str:type_ddia>/<int:pk>', ddia_verify, name='ddia-verify'),
    path('admit/<str:type_ddia>/<int:pk>', ddia_admit, name='ddia-admit'),
    path('validate/<str:type_ddia>/<int:pk>', ddia_validate, name='ddia-validate'),
    path('approve/<str:type_ddia>/<int:pk>', ddia_approve, name='ddia-approve'),
    path('sourceagent/listDDIA/waited/', listDDIA_inwaiting_for_initiator_view, name='listDDIAwaited-sourceagent'),
    path('sourceagent/listDDIA/processed/<str:type_ddia>', listDDIA_processed_for_initiator_view, name='listDDIAprocessed-sourceagent'),
    path('sourceagent/stats/', get_stats_datas_for_source, name='stats-sourceagent'),
    path('verifsource/listDDIA/waited/<str:type_ddia>', listDDIA_inwaiting_for_sourceverifier_view, name='listDDIAwaited-verifsource'),
    path('verifsource/listDDIA/processed/<str:type_ddia>', listDDIA_processed_for_sourceverifier_view, name='listDDIAprocessed-verifsource'),
    path('verifsource/stats/', get_stats_datas_for_sourceverifier, name='stats-verifsource'),
    path('localinfsource/listDDIA/processed/<str:type_ddia>', listDDIA_processed_for_source_localinformer_view, name='listDDIAprocessed-localinfsource'),
    path('sourcestructure/listDDIA/waited/<str:type_ddia>', listDDIA_inwaiting_for_sourcestructure_view, name='listDDIAwaited-sourcestructure'),
    path('sourcestructure/listDDIA/processed/<str:type_ddia>', listDDIA_processed_for_sourcestructure_view, name='listDDIAprocessed-sourcestructure'),
    path('sourcestructure/stats/', get_stats_datas_for_sourcestructure, name='stats-sourcestructure'),
    path('localinformer/listDDIA/waited/<str:type_ddia>', listDDIA_inwaiting_for_authoritylocalinformer_view, name='listDDIAwaited-localinformer'),
    path('localinformer/listDDIA/processed/<str:type_ddia>', listDDIA_processed_for_authoritylocalinformer_view, name='listDDIAprocessed-localinformer'),
    path('localinformer/stats/', get_stats_datas_for_localinformer, name='stats-localinformer'),
    path('nationalinformer/listDDIA/waited/<str:type_ddia>', listDDIA_inwaiting_for_nationalinf_view, name='listDDIAwaited-nationalinformer'),
    path('nationalinformer/listDDIA/processed/<str:type_ddia>', listDDIA_processed_for_nationalinf_view, name='listDDIAprocessed-nationalinformer'),
    path('nationalinformer/stats/', get_stats_datas_for_nationalinformer, name='stats-nationalinformer'),

    path('', include(router.urls)),
]
