from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),

    path("client/", views.client_dashboard_view, name="client_dashboard"),
    path("employee/", views.employee_dashboard_view, name="employee_dashboard"),
]
