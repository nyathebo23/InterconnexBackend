from django.db import router
from django.urls import path, include
from .views import *
from .ddiaviewsets import *
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

aic_create = DemandeAICViewSet.as_view({'post': 'create'})
notam_create = DemandeNOTAMViewSet.as_view({'post': 'create'})
suppaip_create = DemandeSUPPViewSet.as_view({'post': 'create'})
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
    path('submittoverif/<str:type_ddia>/<int:pk>', ddia_submittoverif, name='ddia-submittoverify'),
    path('verify/<str:type_ddia>/<int:pk>', ddia_verify, name='ddia-verify'),
    path('admit/<str:type_ddia>/<int:pk>', ddia_admit, name='ddia-admit'),
    path('validate/<str:type_ddia>/<int:pk>', ddia_validate, name='ddia-validate'),
    path('approve/<str:type_ddia>/<int:pk>', ddia_approve, name='ddia-approve'),
    path('verifsource/listDDIA/waited/<str:type_ddia>', listDDIA_inwaiting_for_sourceverifier_view, name='listDDIAwaited-verifsource'),
    path('verifsource/listDDIA/processed/<str:type_ddia>', listDDIA_processed_for_sourceverifier_view, name='listDDIAprocessed-verifsource'),
    path('', include(router.urls)),
]
