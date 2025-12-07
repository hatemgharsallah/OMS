from django.urls import path

from .views import (
    FulfillmentRequestCreateView,
    InvoiceCreateView,
    OrderCreateView,
    OrderUpdateView,
)

urlpatterns = [
    path("orders/create", OrderCreateView.as_view(), name="order-create"),
    path("orders/update/<int:pk>", OrderUpdateView.as_view(), name="order-update"),
    path("oms/invoice", InvoiceCreateView.as_view(), name="invoice-create"),
    path("oms/fulfillment", FulfillmentRequestCreateView.as_view(), name="fulfillment-create"),
]
