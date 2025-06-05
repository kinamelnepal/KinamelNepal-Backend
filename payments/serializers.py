from rest_framework import serializers
from .models import Payment
from orders.models import Order
# from orders.serializers import OrderSerializer
from core.serializers import BaseModelSerializer
from products.utils.currency import get_exchange_rate, CURRENCY_TO_SYMBOL_MAPPING


class PaymentSerializer(BaseModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(
        source='order', queryset=Order.objects.all(), write_only=True
    )
    # order = OrderSerializer(read_only=True)

    currency = serializers.SerializerMethodField()
    currency_symbol = serializers.SerializerMethodField()
    amount_converted = serializers.SerializerMethodField()
    tax_amount_converted = serializers.SerializerMethodField()
    total_amount_converted = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'uuid', 'order_id', 'method', 'payment_status',
            'amount', 'amount_converted', 'tax_amount', 'tax_amount_converted',
            'total_amount', 'total_amount_converted', 'transaction_id', 'gateway_response',
            'paid_at', 'product_code', 'signed_field_names', 'signature',
            'card_last4', 'card_brand', 'notes',
            'currency', 'currency_symbol', 'created_at', 'updated_at',
        ]

    def get_currency(self, obj):
        return self.context.get('currency', 'NPR')

    def get_currency_symbol(self, obj):
        currency = self.get_currency(obj).upper()
        return CURRENCY_TO_SYMBOL_MAPPING.get(currency, 'Rs')

    def convert_amount(self, amount):
        currency = self.get_currency(None).upper()
        rate = get_exchange_rate(currency)
        return round(float(amount) * rate, 2) if amount is not None else None

    def get_amount_converted(self, obj):
        return self.convert_amount(obj.amount)

    def get_tax_amount_converted(self, obj):
        return self.convert_amount(obj.tax_amount)

    def get_total_amount_converted(self, obj):
        return self.convert_amount(obj.total_amount)

    def validate_payment_status(self, value):
        valid_choices = dict(Payment.STATUS_CHOICES).keys()
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid payment status. Valid options are: {', '.join(valid_choices)}"
            )
        return value

    def validate_method(self, value):
        valid_choices = dict(Payment.PAYMENT_METHOD_CHOICES).keys()
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid payment method. Valid options are: {', '.join(valid_choices)}"
            )
        return value

    def validate(self, attrs):
        if attrs.get('method') == 'esewa':
            required_fields = ['product_code', 'signed_field_names', 'signature']
            for field in required_fields:
                if not attrs.get(field):
                    raise serializers.ValidationError(
                        f"{field} is required for eSewa payments."
                    )
        if attrs.get('method') == 'card':
            if not attrs.get('card_last4') or not attrs.get('card_brand'):
                raise serializers.ValidationError(
                    "Card metadata (last4 and brand) must be provided for card payments."
                )
        return attrs


class EsewaVerificationSerializer(serializers.Serializer):
    oid = serializers.CharField()
    amt = serializers.DecimalField(max_digits=10, decimal_places=2)
    refId = serializers.CharField() 
