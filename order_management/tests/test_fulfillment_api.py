from rest_framework import status
from rest_framework.test import APITestCase

from order_management.models import FulfillmentRequest, Order


class FulfillmentAPITests(APITestCase):
    def setUp(self):
        self.order = Order.objects.create(
            external_id="FUL-1",
            customer_id="CUST",
            total_amount=100,
            currency="TND",
            status=Order.Status.CONFIRMED,
        )
        self.url = "/api/oms/fulfillment"

    def test_create_fulfillment_success(self):
        response = self.client.post(
            self.url, {"order": self.order.id, "warehouse_code": "WH-SFAX"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FulfillmentRequest.objects.count(), 1)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.FULFILLMENT_REQUESTED)

    def test_create_fulfillment_requires_existing_order(self):
        response = self.client.post(self.url, {"order": 999, "warehouse_code": "WH"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_fulfillment_rejects_invalid_order_status(self):
        self.order.status = Order.Status.PENDING
        self.order.save()
        response = self.client.post(
            self.url, {"order": self.order.id, "warehouse_code": "WH-SFAX"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_fulfillment_rejects_duplicate_request(self):
        self.client.post(self.url, {"order": self.order.id, "warehouse_code": "WH-SFAX"}, format="json")
        response = self.client.post(
            self.url, {"order": self.order.id, "warehouse_code": "WH-SFAX"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
