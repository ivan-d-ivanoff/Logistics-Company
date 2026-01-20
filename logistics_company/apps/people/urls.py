from django.urls import path
from .views import client_list, client_create, client_update, client_delete

urlpatterns = [
    path("", client_list, name="clients"),
    path("create/", client_create, name="client_create"),
    path("<int:pk>/update/", client_update, name="client_update"),
    path("<int:pk>/delete/", client_delete, name="client_delete"),
]
