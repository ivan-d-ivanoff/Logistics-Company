from django.urls import path
from .views import parcel_list, parcel_create, parcel_update, parcel_delete

urlpatterns = [
    path("", parcel_list, name="parcel_list"),
    path("create/", parcel_create, name="parcel_create"),
    path("<int:pk>/update/", parcel_update, name="parcel_update"),
    path("<int:pk>/delete/", parcel_delete, name="parcel_delete"),
]

