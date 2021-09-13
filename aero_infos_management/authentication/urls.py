from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from django.urls import include, path
from rest_framework import routers
from django.conf.urls import url
from .views import *
from .verification import *
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'user/email', ChangeEmailViewset, basename="email")
router.register(r'user/password', PasswordResetViewset, basename="password")
router.register(r'user/signup', SignUpViewset, basename="signup")
urlpatterns = [
    path('user/login/', Login.as_view(), name="create_login"),
    # path('token/obtain/', ObtainTokenPairView.as_view(), name='token_create'),
    # path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('user/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('user/signup/', SignUp.as_view(), name="create_user"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
