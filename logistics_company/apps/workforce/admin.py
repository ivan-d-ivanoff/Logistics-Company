from django.contrib import admin
from .models import Employee
from .forms import EmployeeAdminForm


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeAdminForm
    list_display = ("user", "employee_type", "office", "hire_date", "salary")
    list_filter = ("employee_type", "office")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
