from django.test import TestCase

from order_management.models import FulfillmentRequest, Invoice, Order, OrderItem


class OrderModelTests(TestCase):
    def test_create_order_and_items(self):
        order = Order.objects.create(
            external_id="WEB-1", customer_id="CUST-1", total_amount=100, currency="TND"
        )
        OrderItem.objects.create(
            order=order, product_id="SKU-1", product_name="Product", quantity=1, unit_price=100
        )
        self.assertEqual(order.status, Order.Status.PENDING)
        self.assertEqual(order.items.count(), 1)


class InvoiceModelTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            external_id="WEB-2", customer_id="CUST-2", total_amount=50, currency="TND"
        )

    def test_invoice_defaults(self):
        invoice = Invoice.objects.create(order=self.order, amount=50, payment_method="COD")
        self.assertEqual(invoice.status, Invoice.Status.ISSUED)
        self.assertIsNotNone(invoice.issued_at)


class FulfillmentModelTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            external_id="WEB-3",
            customer_id="CUST-3",
            total_amount=70,
            currency="TND",
            status=Order.Status.CONFIRMED,
        )

    def test_fulfillment_defaults(self):
        fulfillment = FulfillmentRequest.objects.create(order=self.order, warehouse_code="WH-1")
        self.assertEqual(fulfillment.status, FulfillmentRequest.Status.CREATED)
        self.assertIsNotNone(fulfillment.created_at)
