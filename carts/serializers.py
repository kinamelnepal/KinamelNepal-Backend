from rest_framework import serializers
from core.serializers import BaseModelSerializer
from products.serializers import ProductSerializer
from .models import Cart, CartItem
from products.utils.currency import get_exchange_rate, CURRENCY_TO_SYMBOL_MAPPING
from products.models import Product
from users.serializers import UserSerializer
from users.models import User


class CartSerializer(BaseModelSerializer):
    items = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    currency_symbol = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all(),
        source = 'user',
        write_only=True,
        required=False,
        allow_null=True
    )
    class Meta:
        model = Cart
        fields = [
            'id', 'uuid', 'user','user_id', 'session_key', 'items',
            'total_items', 'total_price', 'currency', 'currency_symbol',
            'created_at', 'updated_at',
        ]

    def get_currency(self, obj):
        return self.context.get('currency', 'NPR')

    def get_currency_symbol(self, obj):
        currency = self.get_currency(obj).upper()
        return CURRENCY_TO_SYMBOL_MAPPING.get(currency, 'Rs')

    def get_items(self, obj):
        items = obj.items.all()
        serializer = CartItemSerializer(items, many=True, context=self.context)
        return serializer.data

    def get_total_items(self, obj):
        return obj.total_items()

    def get_total_price(self, obj):
        currency = self.get_currency(obj).upper()
        rate = get_exchange_rate(currency)
        return round(float(obj.total_price()) * rate, 2)

    def validate(self, attrs):
        print(attrs,'attrs')
        print(attrs.get('user'),'user_id')
        if not attrs.get('session_key') and not attrs.get('user'):
            raise serializers.ValidationError("Either session_key or user_id is required.")
        return super().validate(attrs)
    

class CartItemSerializer(BaseModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    subtotal = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    currency_symbol = serializers.SerializerMethodField()
    # cart = CartSerializer(read_only=True)
    cart_id = serializers.PrimaryKeyRelatedField(
        queryset=Cart.objects.all(),
        source='cart',
        write_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            'id', 'uuid', 'product', 'product_id', 'quantity', 'subtotal',
            # 'cart',
            'cart_id',
            'currency', 'currency_symbol',
            'created_at', 'updated_at',
        ]

    def get_subtotal(self, obj):
        currency = self.context.get('currency', 'NPR').upper()
        rate = get_exchange_rate(currency)
        if obj.product and obj.product.new_price:
            return round(float(obj.product.new_price) * obj.quantity * rate, 2)
        return 0

    def get_currency(self, obj):
        return self.context.get('currency', 'NPR')

    def get_currency_symbol(self, obj):
        currency = self.context.get('currency', 'NPR').upper()
        return CURRENCY_TO_SYMBOL_MAPPING.get(currency, 'Rs')
