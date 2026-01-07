from django.urls import path
from . import views

urlpatterns = [
    path("offices/", views.offices, name="offices"),
]
