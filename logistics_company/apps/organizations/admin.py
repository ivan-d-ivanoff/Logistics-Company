from django.contrib import admin

from .models import Company, Office


class OfficeInline(admin.TabularInline):
    model = Office
    extra = 0
    fields = ("name", "code", "phone", "address", "working_hours")
    show_change_link = True


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "bulstat", "phone", "address", "office_count")
    search_fields = ("name", "bulstat", "phone")
    raw_id_fields = ("address",)

    inlines = [OfficeInline]

    @admin.display(description="Offices")
    def office_count(self, obj):
        return obj.offices.count()


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "company", "city", "phone", "working_hours", "employee_count")
    list_filter = ("company", "address__city")
    search_fields = ("name", "code", "phone", "address__city", "address__street")
    raw_id_fields = ("address",)

    fieldsets = (
        (None, {
            "fields": ("company", "name", "code")
        }),
        ("Contact", {
            "fields": ("phone", "address", "working_hours")
        }),
    )

    @admin.display(description="City")
    def city(self, obj):
        return obj.address.city if obj.address else "-"

    @admin.display(description="Employees")
    def employee_count(self, obj):
        return obj.employees.count()
