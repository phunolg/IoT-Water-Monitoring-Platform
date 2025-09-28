from django.urls import path

from . import views
from .views import (
    AdminOnlyAPIView,
    UserProfileAPIView,
    change_password,
    change_user_role,
    health_check,
    latest_reading,
    readings_table_view,
    upload_reading,
)

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("readings/", readings_table_view, name="readings_table"),
    path("admin-dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
    path(
        "password-reset-request/",
        views.password_reset_request,
        name="password_reset_request",
    ),
    path(
        "reset-password/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    path("api/admin/users/", AdminOnlyAPIView.as_view(), name="admin_users_api"),
    path("api/user/profile/", UserProfileAPIView.as_view(), name="user_profile_api"),
    path(
        "api/user/<int:user_id>/change-role/", change_user_role, name="change_user_role"
    ),
    path("api/user/change-password/", change_password, name="change_password_api"),
    path("api/latest-reading/", latest_reading, name="latest-reading"),
    path("api/upload-reading/", upload_reading, name="upload-reading"),
    path("health/", health_check, name="health-check"),
]
