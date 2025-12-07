from rest_framework import generics, serializers, status
from rest_framework.response import Response

from .models import FulfillmentRequest, Invoice, Order
from .serializers import (
    FulfillmentRequestSerializer,
    InvoiceSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)


class OrderCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.prefetch_related("items")
    serializer_class = OrderSerializer


class OrderUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.prefetch_related("items")

    def get_serializer_class(self):
        if self.request.method.lower() == "get":
            return OrderSerializer
        return OrderStatusUpdateSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(OrderSerializer(instance).data, status=status.HTTP_200_OK)


class InvoiceCreateView(generics.ListCreateAPIView):
    queryset = Invoice.objects.select_related("order")
    serializer_class = InvoiceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as exc:
            errors = exc.detail
            if isinstance(errors, dict) and "order" in errors:
                order_errors = errors.get("order")
                if order_errors and any("does not exist" in str(err) for err in order_errors):
                    return Response(errors, status=status.HTTP_404_NOT_FOUND)
            raise
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class FulfillmentRequestCreateView(generics.ListCreateAPIView):
    queryset = FulfillmentRequest.objects.select_related("order")
    serializer_class = FulfillmentRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as exc:
            errors = exc.detail
            if isinstance(errors, dict) and "order" in errors:
                order_errors = errors.get("order")
                if order_errors and any("does not exist" in str(err) for err in order_errors):
                    return Response(errors, status=status.HTTP_404_NOT_FOUND)
            raise
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
