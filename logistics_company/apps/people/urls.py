from django.urls import path
from . import views

urlpatterns = [
    path("clients/", views.clients, name="clients"),
    # Clients CRUD API
    path("api/clients/", views.clients_api_list, name="clients_api_list"),
    path("api/clients/create/", views.clients_api_create, name="clients_api_create"),
    path("api/clients/<int:client_id>/", views.clients_api_get, name="clients_api_get"),
    path("api/clients/<int:client_id>/update/", views.clients_api_update, name="clients_api_update"),
    path("api/clients/<int:client_id>/delete/", views.clients_api_delete, name="clients_api_delete"),
]
