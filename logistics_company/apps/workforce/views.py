from django.shortcuts import render

def employees(request):
    return render(request, "employees/employees.html")
