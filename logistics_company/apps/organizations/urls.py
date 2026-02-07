from django.urls import path
from . import views

urlpatterns = [
    path("offices/", views.offices, name="offices"),
    path("api/offices/", views.offices_api_list, name="offices_api_list"),
    path("api/offices/create/", views.offices_api_create, name="offices_api_create"),
    path("api/offices/<int:office_id>/", views.offices_api_update, name="offices_api_update"),
    path("api/offices/<int:office_id>/delete/", views.offices_api_delete, name="offices_api_delete"),
]
