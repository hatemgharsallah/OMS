from rest_framework import status
from rest_framework.test import APITestCase

from order_management.models import Order


class OrderAPITests(APITestCase):
    def setUp(self):
        self.url = "/api/orders/create"
        self.payload = {
            "external_id": "WEB-ORDER-00123",
            "customer_id": "CUST-999",
            "total_amount": 120.50,
            "currency": "TND",
            "items": [
                {
                    "product_id": "SKU-123",
                    "product_name": "Smartphone X",
                    "quantity": 1,
                    "unit_price": 100.00,
                },
                {
                    "product_id": "SKU-456",
                    "product_name": "Phone Case",
                    "quantity": 1,
                    "unit_price": 20.50,
                },
            ],
        }

    def test_create_order_success(self):
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.get()
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.status, Order.Status.PENDING)

    def test_get_orders_returns_list(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["external_id"], self.payload["external_id"])

    def test_create_order_requires_items(self):
        payload = {**self.payload, "items": []}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_rejects_duplicate_external_id(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_validates_totals(self):
        payload = {**self.payload, "total_amount": 100}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_status_success(self):
        self.client.post(self.url, self.payload, format="json")
        order = Order.objects.get()
        response = self.client.patch(f"/api/orders/update/{order.id}", {"status": Order.Status.CONFIRMED}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CONFIRMED)

    def test_update_order_invalid_status_value(self):
        self.client.post(self.url, self.payload, format="json")
        order = Order.objects.get()
        response = self.client.patch(f"/api/orders/update/{order.id}", {"status": "WRONG"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_invalid_transition(self):
        self.client.post(self.url, self.payload, format="json")
        order = Order.objects.get()
        order.status = Order.Status.COMPLETED
        order.save()
        response = self.client.patch(f"/api/orders/update/{order.id}", {"status": Order.Status.PENDING}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_order_detail(self):
        self.client.post(self.url, self.payload, format="json")
        order = Order.objects.get()
        response = self.client.get(f"/api/orders/update/{order.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], order.id)
        self.assertEqual(response.data["external_id"], self.payload["external_id"])

    def test_update_order_not_found(self):
        response = self.client.patch("/api/orders/update/999", {"status": Order.Status.CONFIRMED}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
