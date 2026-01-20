from django.urls import path
from . import views

# urlpatterns = [
#     path("employees/", views.employees, name="employees"),
# ]

urlpatterns = [
    path("", views.employees, name="employees"),
    path("create/", views.employee_create, name="employee_create"),
    path("<int:pk>/edit/", views.employee_update, name="employee_update"),
    path("<int:pk>/delete/", views.employee_delete, name="employee_delete"),
]

