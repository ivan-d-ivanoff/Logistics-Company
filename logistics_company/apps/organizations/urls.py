from django.urls import path
from . import views

urlpatterns = [

    path("companies/", views.company_list, name="company_list"),
    path("companies/create/", views.company_create, name="company_create"),
    path("companies/<int:pk>/edit/", views.company_edit, name="company_edit"),
    path("companies/<int:pk>/delete/", views.company_delete, name="company_delete"),


    path("offices/", views.office_list, name="offices"),
    path("offices/create/", views.office_create, name="office_create"),
    path("offices/<int:pk>/edit/", views.office_edit, name="office_edit"),
    path("offices/<int:pk>/delete/", views.office_delete, name="office_delete"),
]
