from rest_framework import serializers

from .models import FulfillmentRequest, Invoice, Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product_id", "product_name", "quantity", "unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "external_id",
            "customer_id",
            "status",
            "total_amount",
            "currency",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "created_at", "updated_at"]

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("At least one item is required.")
        return items

    def validate(self, attrs):
        items = attrs.get("items", [])
        total = sum([item["quantity"] * item["unit_price"] for item in items])
        total_amount = attrs.get("total_amount")
        if total_amount is not None and total_amount != total:
            raise serializers.ValidationError("Total amount does not match item totals.")
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        return order


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]

    def validate_status(self, value):
        if value not in Order.Status.values:
            raise serializers.ValidationError("Invalid status value")
        return value

    def validate(self, attrs):
        instance = self.instance
        new_status = attrs.get("status")
        if instance:
            current = instance.status
            allowed_transitions = {
                Order.Status.PENDING: {Order.Status.CONFIRMED, Order.Status.CANCELLED},
                Order.Status.CONFIRMED: {Order.Status.FULFILLMENT_REQUESTED},
                Order.Status.FULFILLMENT_REQUESTED: {Order.Status.COMPLETED, Order.Status.CANCELLED},
                Order.Status.COMPLETED: set(),
                Order.Status.CANCELLED: set(),
            }
            if new_status not in allowed_transitions.get(current, set()):
                raise serializers.ValidationError("Invalid status transition")
        return attrs


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ["id", "order", "amount", "status", "issued_at", "paid_at", "payment_method"]
        read_only_fields = ["id", "status", "issued_at", "paid_at"]

    def validate_amount(self, value):
        order = self.initial_data.get("order")
        if order is None:
            return value
        try:
            order_obj = Order.objects.get(pk=order)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order does not exist")
        if value != order_obj.total_amount:
            raise serializers.ValidationError("Invoice amount must match order total")
        return value

    def validate(self, attrs):
        order = attrs.get("order")
        if not order:
            return attrs
        if hasattr(order, "invoice"):
            raise serializers.ValidationError("Invoice already exists for this order")
        if order.status == Order.Status.CANCELLED:
            raise serializers.ValidationError("Cannot invoice a cancelled order")
        return attrs

    def create(self, validated_data):
        validated_data["status"] = Invoice.Status.ISSUED
        return super().create(validated_data)


class FulfillmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FulfillmentRequest
        fields = ["id", "order", "warehouse_code", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "created_at", "updated_at"]

    def validate(self, attrs):
        order = attrs.get("order")
        if not order:
            return attrs
        if hasattr(order, "fulfillment_request"):
            raise serializers.ValidationError("Fulfillment request already exists")
        if order.status != Order.Status.CONFIRMED:
            raise serializers.ValidationError("Order status does not allow fulfillment")
        return attrs

    def create(self, validated_data):
        fulfillment = super().create(validated_data)
        order = fulfillment.order
        order.status = Order.Status.FULFILLMENT_REQUESTED
        order.save(update_fields=["status"])
        return fulfillment
