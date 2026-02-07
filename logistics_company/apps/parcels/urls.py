from django.urls import path
from . import views

urlpatterns = [
    path("", views.parcels, name="parcels"),
    path("api/track/", views.track_parcel_api, name="track_parcel_api"),
    # CRUD API
    path("api/", views.parcels_api_list, name="parcels_api_list"),
    path("api/create/", views.parcels_api_create, name="parcels_api_create"),
    path("api/<int:parcel_id>/", views.parcels_api_get, name="parcels_api_get"),
    path("api/<int:parcel_id>/update/", views.parcels_api_update, name="parcels_api_update"),
    path("api/<int:parcel_id>/delete/", views.parcels_api_delete, name="parcels_api_delete"),
    path("api/<int:parcel_id>/status/", views.parcels_api_update_status, name="parcels_api_update_status"),
]
