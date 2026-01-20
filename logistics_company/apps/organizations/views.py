from django.shortcuts import render, redirect, get_object_or_404
from .models import Company, Office
from apps.common.models import Address

def offices(request):
    return render(request, "organizations/offices.html")

def company_list(request):
    companies = Company.objects.all()
    return render(request, "organizations/company_list.html", {
        "companies": companies
    })

def company_create(request):
    addresses = Address.objects.all()

    if request.method == "POST":
        Company.objects.create(
            name=request.POST["name"],
            bulstat=request.POST["bulstat"],
            phone=request.POST["phone"],
            address_id=request.POST["address"]
        )
        return redirect("company_list")

    return render(request, "organizations/company_form.html", {
        "addresses": addresses
    })

def company_edit(request, pk):
    company = get_object_or_404(Company, pk=pk)
    addresses = Address.objects.all()

    if request.method == "POST":
        company.name = request.POST["name"]
        company.bulstat = request.POST["bulstat"]
        company.phone = request.POST["phone"]
        company.address_id = request.POST["address"]
        company.save()
        return redirect("company_list")

    return render(request, "organizations/company_form.html", {
        "company": company,
        "addresses": addresses
    })

def company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)

    if request.method == "POST":
        company.delete()
        return redirect("company_list")

    return render(request, "organizations/company_confirm_delete.html", {
        "company": company
    })

def office_list(request):
    offices = Office.objects.select_related("company", "address")
    return render(
        request,
        "organizations/offices.html",
        {"offices": offices},
    )

def office_create(request):
    companies = Company.objects.all()
    addresses = Address.objects.all()

    if request.method == "POST":
        Office.objects.create(
            company_id=request.POST["company"],
            name=request.POST["name"],
            phone=request.POST["phone"],
            address_id=request.POST["address"],
            working_hours=request.POST["working_hours"],
        )
        return redirect("office_list")

    return render(
        request,
        "organizations/office_form.html",
        {
            "companies": companies,
            "addresses": addresses,
        },
    )

def office_edit(request, pk):
    office = get_object_or_404(Office, pk=pk)
    companies = Company.objects.all()
    addresses = Address.objects.all()

    if request.method == "POST":
        office.company_id = request.POST["company"]
        office.name = request.POST["name"]
        office.phone = request.POST["phone"]
        office.address_id = request.POST["address"]
        office.working_hours = request.POST["working_hours"]
        office.save()

        return redirect("office_list")

    return render(
        request,
        "organizations/office_form.html",
        {
            "office": office,
            "companies": companies,
            "addresses": addresses,
        },
    )

def office_delete(request, pk):
    office = get_object_or_404(Office, pk=pk)

    if request.method == "POST":
        office.delete()
        return redirect("office_list")

    return render(
        request,
        "organizations/office_confirm_delete.html",
        {"office": office},
    )




