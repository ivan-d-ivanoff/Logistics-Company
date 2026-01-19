from django import forms
from .models import Employee


class EmployeeAdminForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = "__all__"

    def clean_user(self):
        user = self.cleaned_data["user"]
        if user.role != "EMPLOYEE" and not user.is_superuser:
            raise forms.ValidationError("User must have role EMPLOYEE to be an Employee.")
        return user
