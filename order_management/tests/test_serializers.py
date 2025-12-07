from django.test import TestCase

from order_management.models import FulfillmentRequest, Invoice, Order, OrderItem
from order_management.serializers import (
    FulfillmentRequestSerializer,
    InvoiceSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)


class OrderSerializerTests(TestCase):
    def test_requires_items_and_valid_total(self):
        payload = {
            "external_id": "EXT-1",
            "customer_id": "CUST-1",
            "total_amount": 100,
            "currency": "TND",
            "items": [],
        }
        serializer = OrderSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        payload["items"] = [
            {
                "product_id": "SKU-1",
                "product_name": "Product",
                "quantity": 1,
                "unit_price": 90,
            }
        ]
        serializer = OrderSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        payload["items"][0]["unit_price"] = 100
        serializer = OrderSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class OrderStatusSerializerTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            external_id="EXT-STATUS", customer_id="CUST", total_amount=10, currency="TND"
        )

    def test_invalid_status_value(self):
        serializer = OrderStatusUpdateSerializer(self.order, data={"status": "UNKNOWN"})
        self.assertFalse(serializer.is_valid())

    def test_invalid_transition(self):
        self.order.status = Order.Status.COMPLETED
        self.order.save()
        serializer = OrderStatusUpdateSerializer(self.order, data={"status": Order.Status.PENDING})
        self.assertFalse(serializer.is_valid())

    def test_valid_transition(self):
        serializer = OrderStatusUpdateSerializer(self.order, data={"status": Order.Status.CONFIRMED})
        self.assertTrue(serializer.is_valid())


class InvoiceSerializerTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            external_id="EXT-INV",
            customer_id="CUST",
            total_amount=120,
            currency="TND",
            status=Order.Status.CONFIRMED,
        )

    def test_prevents_duplicate_and_mismatch(self):
        payload = {"order": self.order.id, "amount": 100, "payment_method": "COD"}
        serializer = InvoiceSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        payload["amount"] = 120
        serializer = InvoiceSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        serializer = InvoiceSerializer(data=payload)
        self.assertFalse(serializer.is_valid())

    def test_rejects_cancelled_order(self):
        self.order.status = Order.Status.CANCELLED
        self.order.save()
        payload = {"order": self.order.id, "amount": 120}
        serializer = InvoiceSerializer(data=payload)
        self.assertFalse(serializer.is_valid())


class FulfillmentSerializerTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            external_id="EXT-FUL",
            customer_id="CUST",
            total_amount=50,
            currency="TND",
            status=Order.Status.CONFIRMED,
        )

    def test_requires_valid_order_status_and_singleton(self):
        payload = {"order": self.order.id, "warehouse_code": "WH-1"}
        serializer = FulfillmentRequestSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        serializer = FulfillmentRequestSerializer(data=payload)
        self.assertFalse(serializer.is_valid())

    def test_rejects_non_confirmed(self):
        self.order.status = Order.Status.PENDING
        self.order.save()
        payload = {"order": self.order.id, "warehouse_code": "WH-1"}
        serializer = FulfillmentRequestSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
