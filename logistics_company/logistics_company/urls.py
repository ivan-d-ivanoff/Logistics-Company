from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("apps.common.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("parcels/", include("apps.parcels.urls")),
    path("people/", include("apps.people.urls")),
    path("workforce/", include("apps.workforce.urls")),
    path("organizations/", include("apps.organizations.urls")),
]

