from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        CONFIRMED = "CONFIRMED"
        CANCELLED = "CANCELLED"
        FULFILLMENT_REQUESTED = "FULFILLMENT_REQUESTED"
        COMPLETED = "COMPLETED"

    external_id = models.CharField(max_length=64, unique=True, help_text="Order id from the e-commerce system.")
    customer_id = models.CharField(max_length=64, help_text="Reference to the customer in the e-commerce/CRM.")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="TND")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.external_id} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product_id = models.CharField(max_length=64)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Item {self.product_name} x{self.quantity}"


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT"
        ISSUED = "ISSUED"
        PAID = "PAID"
        CANCELLED = "CANCELLED"

    order = models.OneToOneField(Order, related_name="invoice", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ISSUED)
    issued_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=16, default="COD", help_text="Payment method (e.g., COD, ONLINE).")

    def __str__(self):
        return f"Invoice for {self.order_id} ({self.status})"


class FulfillmentRequest(models.Model):
    class Status(models.TextChoices):
        CREATED = "CREATED"
        SENT_TO_WMS = "SENT_TO_WMS"
        COMPLETED = "COMPLETED"
        REJECTED = "REJECTED"

    order = models.OneToOneField(Order, related_name="fulfillment_request", on_delete=models.CASCADE)
    warehouse_code = models.CharField(max_length=32, help_text="Identifier for the warehouse that will fulfill this order.")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Fulfillment for {self.order_id} ({self.status})"
