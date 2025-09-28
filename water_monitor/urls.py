from django.contrib import admin
from django.urls import path, include
from monitoring import views as monitoring_views
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", monitoring_views.home_view, name="home"),
    path("register/", monitoring_views.register_view, name="register"),
    path("login/", monitoring_views.login_view, name="login"),
    path("logout/", monitoring_views.logout_view, name="logout"),
    path("dashboard/",
         monitoring_views.dashboard_view,
         name="dashboard"),
    path("admin-dashboard/",
         monitoring_views.admin_dashboard_view,
         name="admin_dashboard"),
    path("password-reset-request/",
         monitoring_views.password_reset_request,
         name="password_reset_request"),
    path("reset-password/<uidb64>/<token>/",
         monitoring_views.password_reset_confirm,
         name="password_reset_confirm"),
    path("password-reset/", include("django.contrib.auth.urls")),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/',
         SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
    path('api/redoc/',
         SpectacularRedocView.as_view(url_name='schema'),
         name='redoc'),
    path('', include('monitoring.urls')),
]
