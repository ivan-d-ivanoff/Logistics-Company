from django.urls import path

from . import views
from apps.people import views as client_views
from apps.parcels import views as parcels_views
from apps.workforce import views as workforce_views


urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("reports/", views.reports, name="reports"),
    path("track/", views.track, name="track"),
    path("reports/client/", client_views.clients_report, name="reports_client"),
    path(
        "reports/client-parcels/<str:role>/",
        parcels_views.client_parcels_report,
        name="reports_client_parcels_all",
    ),
    path(
        "reports/client-parcels/<int:client_id>/<str:role>/",
        parcels_views.client_parcels_report,
        name="reports_client_parcels",
    ),
    path(
        "reports/employees/",
        workforce_views.employees_report,
        name="reports_employees",
    ),
    path(
        "reports/parcels-by-employee/",
        parcels_views.parcels_by_employee_report,
        name="reports_parcels_by_employee_all",
    ),
    path(
        "reports/parcels-by-employee/<int:employee_id>/",
        parcels_views.parcels_by_employee_report,
        name="reports_parcels_by_employee",
    ),
    path(
        "reports/pending-deliveries/",
        parcels_views.pending_deliveries_report,
        name="reports_pending_deliveries",
    ),
    path(
        "reports/income/",
        parcels_views.income_report,
        name="reports_income",
    ),
]
