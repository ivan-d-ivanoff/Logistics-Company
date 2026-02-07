from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.common.models import Address, Tariff, DeliveryType
from apps.organizations.models import Company, Office
from apps.parcels.models import Parcel, ParcelStatus, ParcelStatusHistory, ParcelNote
from apps.workforce.models import Employee


class Command(BaseCommand):
    help = "Seed database with static sample data for POC"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Clear existing data")

    def handle(self, *args, **options):
        if options["clear"]:
            self.clear_data()
        with transaction.atomic():
            self.seed_data()
        self.stdout.write(self.style.SUCCESS("Seed complete."))

    def clear_data(self):
        ParcelNote.objects.all().delete()
        ParcelStatusHistory.objects.all().delete()
        Parcel.objects.all().delete()
        ParcelStatus.objects.all().delete()
        Employee.objects.all().delete()
        Tariff.objects.all().delete()
        Office.objects.all().delete()
        Company.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Address.objects.all().delete()

    def seed_data(self):
        self._create_admin()
        addresses = self._create_addresses()
        company = self._create_company(addresses)
        tariffs = self._create_tariffs(company)
        offices = self._create_offices(company, addresses)
        statuses = self._create_parcel_statuses()
        employees = self._create_employees(offices)
        clients = self._create_clients(addresses)
        self._create_parcels(company, clients, offices, statuses, employees, tariffs)

    def _create_addresses(self):
        data = [
            {"country": "Bulgaria", "city": "Sofia",   "postal_code": "1000", "street": "Vitosha Blvd 1",       "details": "Floor 2"},
            {"country": "Bulgaria", "city": "Sofia",   "postal_code": "1113", "street": "Tsarigradsko Shose 1", "details": "Building A"},
            {"country": "Bulgaria", "city": "Plovdiv", "postal_code": "4000", "street": "Main Street 1",        "details": ""},
            {"country": "Bulgaria", "city": "Varna",   "postal_code": "9000", "street": "Main Blvd 1",          "details": "Near beach"},
            {"country": "Bulgaria", "city": "Burgas",  "postal_code": "8000", "street": "Bul Bulgaria 1",       "details": ""},
            {"country": "Bulgaria", "city": "Ruse",    "postal_code": "7000", "street": "Ul Ruse 1",            "details": "Center"},
        ]
        return [Address.objects.get_or_create(**d)[0] for d in data]

    def _create_company(self, addresses):
        return Company.objects.get_or_create(
            name="Express Logistics BG",
            defaults={"bulstat": "BG123456789", "phone": "+359 2 123 4567", "address": addresses[0]},
        )[0]

    def _create_tariffs(self, company):
        """Create tariffs for STANDARD and EXPRESS delivery types."""
        tariffs = {}
        tariff_data = [
            {"delivery_type": DeliveryType.STANDARD, "price_per_kg": 5.00},
            {"delivery_type": DeliveryType.EXPRESS, "price_per_kg": 8.50},
        ]
        for data in tariff_data:
            tariff, _ = Tariff.objects.get_or_create(
                company=company,
                delivery_type=data["delivery_type"],
                defaults={"price_per_kg": data["price_per_kg"]},
            )
            tariffs[data["delivery_type"]] = tariff
        return tariffs

    def _create_offices(self, company, addresses):
        data = [
            {"name": "Sofia Central",  "code": "SOF-C", "phone": "+359 2 111 1111", "address": addresses[0], "working_hours": "08:00-20:00"},
            {"name": "Sofia East",     "code": "SOF-E", "phone": "+359 2 222 2222", "address": addresses[1], "working_hours": "09:00-18:00"},
            {"name": "Plovdiv Office", "code": "PLV-1", "phone": "+359 32 333 333", "address": addresses[2], "working_hours": "08:30-17:30"},
            {"name": "Varna Office",   "code": "VAR-1", "phone": "+359 52 444 444", "address": addresses[3], "working_hours": "09:00-18:00"},
        ]
        offices = []
        for d in data:
            office, _ = Office.objects.get_or_create(
                company=company,
                code=d["code"],
                defaults={
                    "name": d["name"],
                    "phone": d["phone"],
                    "address": d["address"],
                    "working_hours": d["working_hours"],
                },
            )
            offices.append(office)
        return offices

    def _create_parcel_statuses(self):
        data = [
            ("CREATED",          "Created",          "Parcel created",      False),
            ("IN_TRANSIT",       "In Transit",       "Parcel in transit",   False),
            ("OUT_FOR_DELIVERY", "Out for Delivery", "Out for delivery",    False),
            ("DELIVERED",        "Delivered",        "Parcel delivered",    True),
            ("RETURNED",         "Returned",         "Returned to sender",  True),
            ("CANCELLED",        "Cancelled",        "Parcel cancelled",    True),
        ]
        return {
            code: ParcelStatus.objects.get_or_create(
                code=code,
                defaults={"name": name, "description": desc, "is_terminal": is_terminal},
            )[0]
            for code, name, desc, is_terminal in data
        }

    def _create_employees(self, offices):
        data = [
            {
                "username": "manager1",
                "first_name": "Ivan",
                "last_name": "Petrov",
                "email": "ivan@test.bg",
                "phone": "+359 888 111 111",
                "employee_code": "EMP-001",
                "employee_type": "MANAGER",
                "office": offices[0],
                "salary": 3500.00,
            },
            {
                "username": "office1",
                "first_name": "Maria",
                "last_name": "Georgieva",
                "email": "maria@test.bg",
                "phone": "+359 888 222 222",
                "employee_code": "EMP-002",
                "employee_type": "OFFICE",
                "office": offices[0],
                "salary": 2000.00,
            },
            {
                "username": "office2",
                "first_name": "Petar",
                "last_name": "Ivanov",
                "email": "petar@test.bg",
                "phone": "+359 888 333 333",
                "employee_code": "EMP-003",
                "employee_type": "OFFICE",
                "office": offices[1],
                "salary": 2000.00,
            },
            {
                "username": "courier1",
                "first_name": "Georgi",
                "last_name": "Dimitrov",
                "email": "georgi@test.bg",
                "phone": "+359 888 444 444",
                "employee_code": "EMP-004",
                "employee_type": "COURIER",
                "office": offices[0],
                "salary": 1800.00,
            },
        ]

        employees = []
        for d in data:
            user, created = User.objects.get_or_create(
                username=d["username"],
                defaults={
                    "first_name": d["first_name"],
                    "last_name": d["last_name"],
                    "email": d["email"],
                    "phone": d["phone"],
                    "role": UserRole.EMPLOYEE,
                },
            )
            if created:
                user.set_password("employee123")
                user.save()

            emp, _ = Employee.objects.get_or_create(
                user=user,
                defaults={
                    "employee_code": d["employee_code"],
                    "employee_type": d["employee_type"],
                    "office": d["office"],
                    "hire_date": date(2024, 10, 1),
                    "salary": d["salary"],
                },
            )
            employees.append(emp)

        return employees

    def _create_clients(self, addresses):
        data = [
            {"username": "client1", "first_name": "Anna",   "last_name": "Koleva",   "email": "anna@mail.bg",   "phone": "+359 899 111 111", "address": addresses[4]},
            {"username": "client2", "first_name": "Stefan", "last_name": "Marinov",  "email": "stefan@mail.bg", "phone": "+359 899 222 222", "address": addresses[5]},
            {"username": "client3", "first_name": "Elena",  "last_name": "Todorova", "email": "elena@mail.bg",  "phone": "+359 899 333 333", "address": addresses[0]},
            {"username": "client4", "first_name": "Viktor", "last_name": "Petkov",   "email": "viktor@mail.bg", "phone": "+359 899 444 444", "address": addresses[1]},
        ]

        clients = []
        for d in data:
            user, created = User.objects.get_or_create(
                username=d["username"],
                defaults={
                    "first_name": d["first_name"],
                    "last_name": d["last_name"],
                    "email": d["email"],
                    "phone": d["phone"],
                    "role": UserRole.CLIENT,
                    "default_address": d["address"],
                    "preferred_address": d["address"],
                },
            )
            if created:
                user.set_password("client123")
                user.save()

            clients.append(user)

        return clients

    def _create_admin(self):
        """Create an admin user for testing."""
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "first_name": "Admin",
                "last_name": "User",
                "email": "admin@test.bg",
                "phone": "+359 888 000 000",
                "role": UserRole.ADMIN,
            },
        )
        if created:
            admin.set_password("admin123")
            admin.save()
        return admin

    def _create_parcels(self, company, clients, offices, statuses, employees, tariffs):
        if len(clients) < 2:
            return

        office_staff = [e for e in employees if e.employee_type in ("OFFICE", "MANAGER")]
        courier = next((e for e in employees if e.employee_type == "COURIER"), None)
        staff = office_staff[0] if office_staff else None

        now = timezone.now()
        from datetime import timedelta

        data = [
            # Parcel 1: Just created
            {
                "tracking_number": "EXP202600000001",
                "company": company,
                "sender": clients[0],
                "receiver": clients[1],
                "sender_office": offices[0],
                "receiver_office": offices[1],
                "pickup_address": clients[0].default_address,
                "delivery_address": clients[1].default_address,
                "weight_kg": Decimal("1.500"),
                "delivery_type": DeliveryType.STANDARD,
                "tariff": tariffs[DeliveryType.STANDARD],
                "current_status": statuses["CREATED"],
                "delivered_at": None,
            },
            # Parcel 2: In transit
            {
                "tracking_number": "EXP202600000002",
                "company": company,
                "sender": clients[1],
                "receiver": clients[2],
                "sender_office": offices[1],
                "receiver_office": offices[2],
                "pickup_address": clients[1].default_address,
                "delivery_address": clients[2].default_address,
                "weight_kg": Decimal("3.200"),
                "delivery_type": DeliveryType.EXPRESS,
                "tariff": tariffs[DeliveryType.EXPRESS],
                "current_status": statuses["IN_TRANSIT"],
                "delivered_at": None,
            },
            # Parcel 3: Delivered
            {
                "tracking_number": "EXP202600000003",
                "company": company,
                "sender": clients[2],
                "receiver": clients[3],
                "sender_office": offices[2],
                "receiver_office": offices[3],
                "pickup_address": clients[2].default_address,
                "delivery_address": clients[3].default_address,
                "weight_kg": Decimal("0.800"),
                "delivery_type": DeliveryType.STANDARD,
                "tariff": tariffs[DeliveryType.STANDARD],
                "current_status": statuses["DELIVERED"],
                "delivered_at": now - timedelta(days=2),
            },
            # Parcel 4: Out for delivery
            {
                "tracking_number": "EXP202600000004",
                "company": company,
                "sender": clients[3],
                "receiver": clients[0],
                "sender_office": offices[3],
                "receiver_office": offices[0],
                "pickup_address": clients[3].default_address,
                "delivery_address": clients[0].default_address,
                "weight_kg": Decimal("2.100"),
                "delivery_type": DeliveryType.EXPRESS,
                "tariff": tariffs[DeliveryType.EXPRESS],
                "current_status": statuses["OUT_FOR_DELIVERY"],
                "delivered_at": None,
            },
            # Parcel 5: Returned
            {
                "tracking_number": "EXP202600000005",
                "company": company,
                "sender": clients[0],
                "receiver": clients[2],
                "sender_office": offices[0],
                "receiver_office": offices[2],
                "pickup_address": clients[0].default_address,
                "delivery_address": clients[2].default_address,
                "weight_kg": Decimal("5.000"),
                "delivery_type": DeliveryType.STANDARD,
                "tariff": tariffs[DeliveryType.STANDARD],
                "current_status": statuses["RETURNED"],
                "delivered_at": None,
            },
            # Parcel 6: Cancelled
            {
                "tracking_number": "EXP202600000006",
                "company": company,
                "sender": clients[1],
                "receiver": clients[3],
                "sender_office": offices[1],
                "receiver_office": offices[3],
                "pickup_address": clients[1].default_address,
                "delivery_address": clients[3].default_address,
                "weight_kg": Decimal("0.500"),
                "delivery_type": DeliveryType.STANDARD,
                "tariff": tariffs[DeliveryType.STANDARD],
                "current_status": statuses["CANCELLED"],
                "delivered_at": None,
            },
            # Parcel 7: Another delivered (for income reports)
            {
                "tracking_number": "EXP202600000007",
                "company": company,
                "sender": clients[2],
                "receiver": clients[0],
                "sender_office": offices[2],
                "receiver_office": offices[0],
                "pickup_address": clients[2].default_address,
                "delivery_address": clients[0].default_address,
                "weight_kg": Decimal("4.500"),
                "delivery_type": DeliveryType.EXPRESS,
                "tariff": tariffs[DeliveryType.EXPRESS],
                "current_status": statuses["DELIVERED"],
                "delivered_at": now - timedelta(days=5),
            },
        ]

        for d in data:
            parcel, created = Parcel.objects.get_or_create(
                tracking_number=d["tracking_number"],
                defaults={**d, "registered_by": staff},
            )
            if created:
                # Create initial status history
                ParcelStatusHistory.objects.create(
                    parcel=parcel,
                    status=statuses["CREATED"],
                    office=d["sender_office"],
                    changed_by=staff,
                    note="Parcel registered",
                    created_at=now - timedelta(days=7),
                )

        # Add richer status history for parcels with multiple status changes
        self._add_status_history(statuses, offices, employees, now)

    def _add_status_history(self, statuses, offices, employees, now):
        """Add detailed status history for demonstration."""
        from datetime import timedelta

        staff = employees[0] if employees else None
        courier = next((e for e in employees if e.employee_type == "COURIER"), staff)

        # Parcel 2 (IN_TRANSIT): CREATED -> IN_TRANSIT
        try:
            p2 = Parcel.objects.get(tracking_number="EXP202600000002")
            if p2.status_history.count() == 1:
                ParcelStatusHistory.objects.create(
                    parcel=p2, status=statuses["IN_TRANSIT"], office=offices[1],
                    changed_by=staff, note="Picked up from sender office",
                    created_at=now - timedelta(days=1),
                )
        except Parcel.DoesNotExist:
            pass

        # Parcel 3 (DELIVERED): CREATED -> IN_TRANSIT -> OUT_FOR_DELIVERY -> DELIVERED
        try:
            p3 = Parcel.objects.get(tracking_number="EXP202600000003")
            if p3.status_history.count() == 1:
                ParcelStatusHistory.objects.create(
                    parcel=p3, status=statuses["IN_TRANSIT"], office=offices[2],
                    changed_by=staff, note="In transit to destination",
                    created_at=now - timedelta(days=5),
                )
                ParcelStatusHistory.objects.create(
                    parcel=p3, status=statuses["OUT_FOR_DELIVERY"], office=offices[3],
                    changed_by=courier, note="Out for delivery",
                    created_at=now - timedelta(days=3),
                )
                ParcelStatusHistory.objects.create(
                    parcel=p3, status=statuses["DELIVERED"], office=offices[3],
                    changed_by=courier, note="Delivered to recipient",
                    created_at=now - timedelta(days=2),
                )
        except Parcel.DoesNotExist:
            pass

        # Parcel 4 (OUT_FOR_DELIVERY): CREATED -> IN_TRANSIT -> OUT_FOR_DELIVERY
        try:
            p4 = Parcel.objects.get(tracking_number="EXP202600000004")
            if p4.status_history.count() == 1:
                ParcelStatusHistory.objects.create(
                    parcel=p4, status=statuses["IN_TRANSIT"], office=offices[3],
                    changed_by=staff, note="Shipped from Varna",
                    created_at=now - timedelta(days=2),
                )
                ParcelStatusHistory.objects.create(
                    parcel=p4, status=statuses["OUT_FOR_DELIVERY"], office=offices[0],
                    changed_by=courier, note="Courier assigned for delivery",
                    created_at=now - timedelta(hours=3),
                )
        except Parcel.DoesNotExist:
            pass

        # Parcel 5 (RETURNED): CREATED -> IN_TRANSIT -> OUT_FOR_DELIVERY -> RETURNED
        try:
            p5 = Parcel.objects.get(tracking_number="EXP202600000005")
            if p5.status_history.count() == 1:
                ParcelStatusHistory.objects.create(
                    parcel=p5, status=statuses["IN_TRANSIT"], office=offices[0],
                    changed_by=staff, note="Shipped",
                    created_at=now - timedelta(days=4),
                )
                ParcelStatusHistory.objects.create(
                    parcel=p5, status=statuses["OUT_FOR_DELIVERY"], office=offices[2],
                    changed_by=courier, note="Delivery attempt",
                    created_at=now - timedelta(days=2),
                )
                ParcelStatusHistory.objects.create(
                    parcel=p5, status=statuses["RETURNED"], office=offices[0],
                    changed_by=staff, note="Recipient not available after 3 attempts",
                    created_at=now - timedelta(days=1),
                )
        except Parcel.DoesNotExist:
            pass

        # Parcel 6 (CANCELLED): CREATED -> CANCELLED
        try:
            p6 = Parcel.objects.get(tracking_number="EXP202600000006")
            if p6.status_history.count() == 1:
                ParcelStatusHistory.objects.create(
                    parcel=p6, status=statuses["CANCELLED"], office=offices[1],
                    changed_by=staff, note="Cancelled by sender request",
                    created_at=now - timedelta(days=3),
                )
        except Parcel.DoesNotExist:
            pass

        # Add notes to some parcels
        self._add_parcel_notes(now)

    def _add_parcel_notes(self, now):
        """Add sample notes to parcels."""
        from datetime import timedelta

        try:
            p4 = Parcel.objects.get(tracking_number="EXP202600000004")
            if not p4.notes.exists():
                ParcelNote.objects.create(
                    parcel=p4,
                    note_type=ParcelNote.NoteType.DELIVERY,
                    content="Please call before delivery. Customer prefers afternoon delivery.",
                    created_at=now - timedelta(days=1),
                )
        except Parcel.DoesNotExist:
            pass

        try:
            p5 = Parcel.objects.get(tracking_number="EXP202600000005")
            if not p5.notes.exists():
                ParcelNote.objects.create(
                    parcel=p5,
                    note_type=ParcelNote.NoteType.ISSUE,
                    content="Multiple delivery attempts failed. Recipient not home.",
                    created_at=now - timedelta(days=2),
                )
        except Parcel.DoesNotExist:
            pass
