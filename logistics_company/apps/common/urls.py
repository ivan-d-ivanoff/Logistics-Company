from django.urls import path

from . import views
from apps.people import views as client_views
from apps.parcels import views as received_views


urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("reports/", views.reports, name="reports"),
    path("track/", views.track, name="track"),
    path("reports/client/", client_views.clients_report, name="reports_client"),
    path(
        "reports/client-parcels/<str:role>/",
        received_views.client_parcels_report,
        name="reports_client_parcels_all",
    ),
    path(
        "reports/client-parcels/<int:client_id>/<str:role>/",
        received_views.client_parcels_report,
        name="reports_client_parcels",
    ),
]
