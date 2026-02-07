from django.urls import path
from . import views

urlpatterns = [
    path("employees/", views.employees, name="employees"),
    path("api/employees/", views.employees_api_list, name="employees_api_list"),
    path("api/employees/create/", views.employees_api_create, name="employees_api_create"),
    path("api/employees/<int:employee_id>/", views.employees_api_update, name="employees_api_update"),
    path("api/employees/<int:employee_id>/delete/", views.employees_api_delete, name="employees_api_delete"),
]
