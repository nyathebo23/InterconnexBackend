from django.db import router
from django.urls import path, include
from .views import *
from .ddia_viewsets import *
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

aic_create = DemandeAICViewSet.as_view({'post': 'create'})
notam_create = DemandeNOTAMViewSet.as_view({'post': 'create'})
suppaip_create = DemandeSUPPViewSet.as_view({'post': 'create'})
aic_update = DemandeAICViewSet.as_view({'post': 'update'})
notam_update = DemandeNOTAMViewSet.as_view({'post': 'update'})
suppaip_update = DemandeSUPPViewSet.as_view({'post': 'update'})
aic_retrieve = DemandeAICViewSet.as_view({'get': 'retrieve'})
notam_retrieve = DemandeNOTAMViewSet.as_view({'get': 'retrieve'})
suppaip_retrieve = DemandeSUPPViewSet.as_view({'get': 'retrieve'})
ddia_submittoverif = DDIAControlViewset.as_view({'post': 'submittoverif'})
ddia_verify = DDIAControlViewset.as_view({'post': 'verify'})
ddia_admit = DDIAControlViewset.as_view({'post': 'admit'})
ddia_validate = DDIAControlViewset.as_view({'post': 'validate'})
ddia_approve = DDIAControlViewset.as_view({'post': 'approve'})

router.register(r'agent', AgentViewSet, basename='agentactions')
router.register(r'local-agent', LocalAgentViewSet, basename='localagentactions')
router.register(r'national-agent', NationalAgentViewSet, basename='nationalagentactions')

router.register(r'units', UnitViewSet)
router.register(r'aerodromes', AerodromeViewSet)
router.register(r'local-informers', LocalInformerViewSet),
router.register(r'national-informers', NationalInformerViewSet)
urlpatterns = [
    # path('source/listDDIA/<str:type_ddia>', )
    path('demande-aic/create', aic_create, name='aic-create'),
    path('demande-notam/create', notam_create, name='notam-create'),
    path('demande-supp/create', suppaip_create, name='supp-create'),
    path('demande-aic/update/<int:pk>', aic_update, name='aic-update'),
    path('demande-notam/update/<int:pk>', notam_update, name='notam-update'),
    path('demande-supp/update/<int:pk>', notam_update, name='supp-update'),
    path('demande-aic/<int:pk>', aic_retrieve, name='demandeaic-detail'),
    path('demande-notam/<int:pk>', notam_retrieve, name='demandenotam-detail'),
    path('demande-supp/<int:pk>', suppaip_retrieve, name='demandesupp-detail'),
    path('submittoverif/<str:type_ddia>/<int:pk>', ddia_submittoverif, name='ddia-submittoverify'),
    path('verify/<str:type_ddia>/<int:pk>', ddia_verify, name='ddia-verify'),
    path('admit/<str:type_ddia>/<int:pk>', ddia_admit, name='ddia-admit'),
    path('validate/<str:type_ddia>/<int:pk>', ddia_validate, name='ddia-validate'),
    path('approve/<str:type_ddia>/<int:pk>', ddia_approve, name='ddia-approve'),
    path('sourceagent/listDDIA/waited/<str:type_ddia>', listDDIA_inwaiting_for_initiator_view, name='listDDIAwaited-sourceagent'),
    path('sourceagent/listDDIA/processed/<str:type_ddia>', listDDIA_processed_for_initiator_view, name='listDDIAprocessed-sourceagent'),
    path('verifsource/listDDIA/waited/<str:type_ddia>', listDDIA_inwaiting_for_sourceverifier_view, name='listDDIAwaited-verifsource'),
    path('verifsource/listDDIA/processed/<str:type_ddia>', listDDIA_processed_for_sourceverifier_view, name='listDDIAprocessed-verifsource'),
    path('sourcestructure/listDDIA/waited/<str:type_ddia>', listDDIA_inwaiting_for_sourcestructure_view, name='listDDIAwaited-sourcestructure'),
    path('sourcestructure/listDDIA/processed/<str:type_ddia>', listDDIA_processed_for_sourcestructure_view, name='listDDIAprocessed-sourcestructure'),
    path('localinformer/listDDIA/waited/<str:type_ddia>', listDDIA_inwaiting_for_authoritylocalinformer_view, name='listDDIAwaited-localinformer'),
    path('localinformer/listDDIA/processed/<str:type_ddia>', listDDIA_processed_for_authoritylocalinformer_view, name='listDDIAprocessed-localinformer'),
    path('nationalinformer/listDDIA/waited/<str:type_ddia>', listDDIA_inwaiting_for_nationalinf_view, name='listDDIAwaited-nationalinformer'),
    path('nationalinformer/listDDIA/processed/<str:type_ddia>', listDDIA_processed_for_nationalinf_view, name='listDDIAprocessed-nationalinformer'),
    path('', include(router.urls)),
]
