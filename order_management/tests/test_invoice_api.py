from rest_framework import status
from rest_framework.test import APITestCase

from order_management.models import Invoice, Order


class InvoiceAPITests(APITestCase):
    def setUp(self):
        self.order = Order.objects.create(
            external_id="INV-1",
            customer_id="CUST",
            total_amount=120.50,
            currency="TND",
            status=Order.Status.CONFIRMED,
        )
        self.url = "/api/oms/invoice"

    def test_create_invoice_success(self):
        response = self.client.post(
            self.url,
            {"order": self.order.id, "amount": 120.50, "payment_method": "COD"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Invoice.objects.count(), 1)

    def test_create_invoice_requires_existing_order(self):
        response = self.client.post(self.url, {"order": 999, "amount": 120.50}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_invoice_rejects_duplicate_for_same_order(self):
        self.client.post(
            self.url, {"order": self.order.id, "amount": 120.50, "payment_method": "COD"}, format="json"
        )
        response = self.client.post(
            self.url, {"order": self.order.id, "amount": 120.50, "payment_method": "COD"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_rejects_cancelled_order(self):
        self.order.status = Order.Status.CANCELLED
        self.order.save()
        response = self.client.post(
            self.url, {"order": self.order.id, "amount": 120.50, "payment_method": "COD"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_validates_amount(self):
        response = self.client.post(
            self.url, {"order": self.order.id, "amount": 100.00, "payment_method": "COD"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_invoices_returns_list(self):
        self.client.post(
            self.url, {"order": self.order.id, "amount": 120.50, "payment_method": "COD"}, format="json"
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["order"], self.order.id)
