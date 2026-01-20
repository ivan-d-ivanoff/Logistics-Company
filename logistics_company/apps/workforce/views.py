from django.shortcuts import render, get_object_or_404, redirect
from django.forms import ModelForm
from django.db import transaction

from .models import Employee
from ..accounts.models import AppUser


class UserForm(ModelForm):
    class Meta:
        model = AppUser
        fields = ("username", "email")


class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = ("employee_type", "office", "hire_date", "salary")


def employee_list(request):
    employees = Employee.objects.select_related("user", "office")
    return render(
        request,
        "employee_list.html",
        {
            "employees": employees
        }
    )


@transaction.atomic
def employee_create(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        employee_form = EmployeeForm(request.POST)

        if user_form.is_valid() and employee_form.is_valid():
            user = user_form.save()

            employee = employee_form.save(commit=False)
            employee.user = user
            employee.save()

            return redirect("employee_list")
    else:
        user_form = UserForm()
        employee_form = EmployeeForm()

    return render(
        request,
        "employee_form.html",
        {
            "user_form": user_form,
            "employee_form": employee_form,
        }
    )


@transaction.atomic
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    user = employee.user

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        employee_form = EmployeeForm(request.POST, instance=employee)

        if user_form.is_valid() and employee_form.is_valid():
            user_form.save()
            employee_form.save()
            return redirect("employee_list")
    else:
        user_form = UserForm(instance=user)
        employee_form = EmployeeForm(instance=employee)

    return render(
        request,
        "employee_form.html",
        {
            "user_form": user_form,
            "employee_form": employee_form,
            "employee": employee,
        }
    )


def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == "POST":
        employee.user.delete()  # cascade → employee
        return redirect("employee_list")

    return render(
        request,
        "employee_confirm_delete.html",
        {
            "employee": employee
        }
    )
