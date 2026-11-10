"""
Management command to seed realistic warehouse inventory, boxes, users, and orders.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from inventory.models import Product, ShippingBox
from orders.models import Order, OrderItem, OrderStatus
from accounts.models import UserProfile, UserRole
from recommendations.views import process_order_recommendation


class Command(BaseCommand):
    help = "Seeds demo products, boxes, users, and sample orders with recommendations."

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo warehouse data...")

        # 1. Users
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@smartbox.local", "is_staff": True, "is_superuser": True}
        )
        admin_user.set_password("admin123")
        admin_user.save()
        if hasattr(admin_user, "profile"):
            admin_user.profile.role = UserRole.ADMIN
            admin_user.profile.save()

        staff_user, _ = User.objects.get_or_create(
            username="warehouse",
            defaults={"email": "staff@smartbox.local"}
        )
        staff_user.set_password("warehouse123")
        staff_user.save()
        if hasattr(staff_user, "profile"):
            staff_user.profile.role = UserRole.WAREHOUSE_STAFF
            staff_user.profile.save()

        self.stdout.write(self.style.SUCCESS("Users created: admin (admin123), warehouse (warehouse123)"))

        # 2. Shipping Boxes
        boxes_data = [
            {"code": "BOX-S", "name": "Small Shipping Box", "length": "25.00", "width": "20.00", "height": "15.00", "max_weight": "5.00", "cost": "12.00"},
            {"code": "BOX-M", "name": "Medium Standard Box", "length": "45.00", "width": "35.00", "height": "20.00", "max_weight": "12.00", "cost": "25.00"},
            {"code": "BOX-L", "name": "Large Shipping Box", "length": "60.00", "width": "45.00", "height": "30.00", "max_weight": "20.00", "cost": "42.00"},
            {"code": "BOX-XL", "name": "Extra Large Heavy Duty", "length": "75.00", "width": "50.00", "height": "45.00", "max_weight": "35.00", "cost": "65.00"},
            {"code": "BOX-FLAT", "name": "Flat Mailer Box", "length": "48.00", "width": "32.00", "height": "8.00", "max_weight": "6.00", "cost": "16.00"},
            {"code": "BOX-HEAVY", "name": "Heavy-Duty Compact Box", "length": "30.00", "width": "30.00", "height": "30.00", "max_weight": "25.00", "cost": "30.00"},
        ]
        created_boxes = {}
        for b in boxes_data:
            box_obj, _ = ShippingBox.objects.update_or_create(
                code=b["code"],
                defaults={
                    "name": b["name"],
                    "length": Decimal(b["length"]),
                    "width": Decimal(b["width"]),
                    "height": Decimal(b["height"]),
                    "max_weight": Decimal(b["max_weight"]),
                    "cost": Decimal(b["cost"]),
                    "is_active": True,
                }
            )
            created_boxes[b["code"]] = box_obj
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_boxes)} shipping boxes."))

        # 3. Products
        products_data = [
            {"sku": "LAPTOP-PRO-15", "name": "Professional 15-inch Laptop", "length": "35.00", "width": "25.00", "height": "2.00", "weight": "2.00"},
            {"sku": "MOUSE-WL-01", "name": "Wireless Ergonomic Mouse", "length": "12.00", "width": "7.00", "height": "4.00", "weight": "0.20"},
            {"sku": "KB-MECH-RGB", "name": "RGB Mechanical Keyboard", "length": "45.00", "width": "15.00", "height": "4.00", "weight": "1.10"},
            {"sku": "HEADPHONES-ST", "name": "Studio Over-Ear Headphones", "length": "20.00", "width": "18.00", "height": "9.00", "weight": "0.45"},
            {"sku": "MUG-CERAMIC", "name": "Ceramic Warehouse Coffee Mug", "length": "11.00", "width": "11.00", "height": "10.00", "weight": "0.35"},
            {"sku": "LAMP-DESK-LED", "name": "Adjustable LED Desk Lamp", "length": "40.00", "width": "15.00", "height": "15.00", "weight": "1.80"},
            {"sku": "MONITOR-27", "name": "27-inch 4K UHD Monitor", "length": "62.00", "width": "38.00", "height": "12.00", "weight": "5.50"},
            {"sku": "BOOK-PYTHON", "name": "Advanced Python & Django Guide", "length": "24.00", "width": "18.00", "height": "3.50", "weight": "0.85"},
        ]
        created_prods = {}
        for p in products_data:
            prod_obj, _ = Product.objects.update_or_create(
                sku=p["sku"],
                defaults={
                    "name": p["name"],
                    "length": Decimal(p["length"]),
                    "width": Decimal(p["width"]),
                    "height": Decimal(p["height"]),
                    "weight": Decimal(p["weight"]),
                    "is_active": True,
                }
            )
            created_prods[p["sku"]] = prod_obj
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_prods)} products."))

        # 4. Sample Orders
        # Order 1: Laptop + Mouse + Keyboard (PRD benchmark)
        order1, _ = Order.objects.get_or_create(
            order_number="ORD-1001",
            defaults={"customer_name": "Apex Tech Solutions", "customer_email": "purchasing@apextech.com", "created_by": staff_user, "status": OrderStatus.PENDING}
        )
        if not order1.items.exists():
            OrderItem.objects.create(order=order1, product=created_prods["LAPTOP-PRO-15"], quantity=1)
            OrderItem.objects.create(order=order1, product=created_prods["MOUSE-WL-01"], quantity=2)
            OrderItem.objects.create(order=order1, product=created_prods["KB-MECH-RGB"], quantity=1)
            # Run recommendation
            process_order_recommendation(order1)

        # Order 2: Multiple smaller items (Headphones + 2 Mugs + Book)
        order2, _ = Order.objects.get_or_create(
            order_number="ORD-1002",
            defaults={"customer_name": "Sarah Connor", "customer_email": "sarah@example.com", "created_by": staff_user, "status": OrderStatus.PENDING}
        )
        if not order2.items.exists():
            OrderItem.objects.create(order=order2, product=created_prods["HEADPHONES-ST"], quantity=1)
            OrderItem.objects.create(order=order2, product=created_prods["MUG-CERAMIC"], quantity=2)
            OrderItem.objects.create(order=order2, product=created_prods["BOOK-PYTHON"], quantity=1)
            process_order_recommendation(order2)

        # Order 3: Monitor (large item)
        order3, _ = Order.objects.get_or_create(
            order_number="ORD-1003",
            defaults={"customer_name": "Design Studio 9", "customer_email": "ops@design9.com", "created_by": staff_user, "status": OrderStatus.PENDING}
        )
        if not order3.items.exists():
            OrderItem.objects.create(order=order3, product=created_prods["MONITOR-27"], quantity=1)
            OrderItem.objects.create(order=order3, product=created_prods["HEADPHONES-ST"], quantity=1)
            process_order_recommendation(order3)

        # Order 4: Pending order awaiting recommendation
        order4, _ = Order.objects.get_or_create(
            order_number="ORD-1004",
            defaults={"customer_name": "Cyberdyne Systems", "customer_email": "logistics@cyberdyne.com", "created_by": staff_user, "status": OrderStatus.PENDING}
        )
        if not order4.items.exists():
            OrderItem.objects.create(order=order4, product=created_prods["LAPTOP-PRO-15"], quantity=2)
            OrderItem.objects.create(order=order4, product=created_prods["MOUSE-WL-01"], quantity=2)

        self.stdout.write(self.style.SUCCESS("Successfully seeded demo orders and generated recommendations!"))

