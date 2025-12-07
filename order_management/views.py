from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import (
    FulfillmentRequestSerializer,
    InvoiceSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)


class OrderCreateView(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderUpdateView(APIView):
    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvoiceCreateView(APIView):
    def post(self, request):
        serializer = InvoiceSerializer(data=request.data)
        if serializer.is_valid():
            invoice = serializer.save()
            return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)
        # differentiate not found
        if isinstance(serializer.errors, dict) and "order" in serializer.errors:
            order_errors = serializer.errors.get("order")
            if order_errors and any("does not exist" in str(err) for err in order_errors):
                return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FulfillmentRequestCreateView(APIView):
    def post(self, request):
        serializer = FulfillmentRequestSerializer(data=request.data)
        if serializer.is_valid():
            fulfillment = serializer.save()
            return Response(
                FulfillmentRequestSerializer(fulfillment).data, status=status.HTTP_201_CREATED
            )
        if isinstance(serializer.errors, dict) and "order" in serializer.errors:
            order_errors = serializer.errors.get("order")
            if order_errors and any("does not exist" in str(err) for err in order_errors):
                return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
