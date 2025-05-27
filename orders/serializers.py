from rest_framework import serializers
from .models import OrderItem
from products.serializers import ProductSerializer
from core.serializers import BaseModelSerializer

from rest_framework import serializers
from .models import Order
from accounts.serializers import AddressSerializer
from products.utils.currency import get_exchange_rate, CURRENCY_TO_SYMBOL_MAPPING
from accounts.models import Address
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from products.models import Product  
from django.utils.crypto import get_random_string
from carts.serializers import CartSerializer
from carts.models import Cart
from carts.models import CartItem  
from orders.models import OrderItem 
from users.serializers import UserSerializer

User = get_user_model()

class OrderSerializer(BaseModelSerializer):
    # items = serializers.SerializerMethodField()
    user_id = serializers.PrimaryKeyRelatedField(source='user',queryset=User.objects.all(),write_only=True)
    user = UserSerializer(read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)
    shipping_address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), source='shipping_address', write_only=True
    )
    billing_address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), source='billing_address', write_only=True, required=False
    )
    currency = serializers.SerializerMethodField()
    currency_symbol = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    shipping_cost = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    cart_id = serializers.PrimaryKeyRelatedField(
        queryset=Cart.objects.all(), source='cart', write_only=True, required=False, allow_null=True
    )
    
    cart = CartSerializer(read_only=True, required=False)
    class Meta:
        model = Order
        fields = [
            'id', 'uuid','slug', 'user','user_id', 'full_name', 'email', 'phone_number', 
            'shipping_address', 'shipping_address_id', 'billing_address', 'billing_address_id', 
            'payment_method', 'payment_status', 'payment_id', 'paid_at', 
            'shipping_cost', 'subtotal', 'tax', 'discount', 'total', 'order_status', 'is_shipped', 
            'shipped_at', 'tracking_number', 'delivery_estimate', 'notes', 'created_at', 'updated_at', 
            'currency', 'currency_symbol','cart_id', 'cart',
            # 'items'
        ]

    def get_currency(self, obj):
        return self.context.get('currency', 'NPR')

    def get_currency_symbol(self, obj):
        currency = self.context.get('currency', 'NPR').upper()
        return CURRENCY_TO_SYMBOL_MAPPING.get(currency, 'Rs')

    def get_subtotal(self, obj):
        currency = self.context.get('currency', 'NPR').upper()
        rate = get_exchange_rate(currency)
        return round(float(obj.subtotal) * rate, 2) if obj.subtotal else None

    def get_total(self, obj):
        currency = self.context.get('currency', 'NPR').upper()
        rate = get_exchange_rate(currency)
        return round(float(obj.total) * rate, 2) if obj.total else None

    def get_shipping_cost(self, obj):
        currency = self.context.get('currency', 'NPR').upper()
        rate = get_exchange_rate(currency)
        return round(float(obj.shipping_cost) * rate, 2) if obj.shipping_cost else None

    def get_discount(self, obj):
        currency = self.context.get('currency', 'NPR').upper()
        rate = get_exchange_rate(currency)
        return round(float(obj.discount) * rate, 2) if obj.discount else None

    # def get_items(self, obj):
    #     items = obj.order_items.all()
    #     serializer = OrderItemSerializer(items, many=True, context=self.context)
    #     return serializer.data

    # Custom Validations
    def validate_total(self, value):
        """
        Ensure that the 'total' is the sum of the subtotal, shipping cost, tax, and discount.
        """
        subtotal = self.initial_data.get('subtotal', 0)
        shipping_cost = self.initial_data.get('shipping_cost', 0)
        tax = self.initial_data.get('tax', 0)
        discount = self.initial_data.get('discount', 0)
        
        calculated_total = float(subtotal) + float(shipping_cost) + float(tax) - float(discount)
        
        if round(calculated_total, 2) != round(value, 2):
            raise serializers.ValidationError("The 'total' does not match the sum of the subtotal, shipping cost, tax, and discount.")
        
        return value

    def validate_payment_status(self, value):
        """
        Ensure that the payment status is one of the valid choices.
        """
        if value not in dict(Order.PAYMENT_STATUS_CHOICES).keys():
            raise serializers.ValidationError(f"Invalid payment status. Valid choices are: {', '.join(dict(Order.PAYMENT_STATUS_CHOICES).keys())}")
        return value

    def validate_payment_method(self, value):
        """
        Ensure that the payment method is one of the valid choices.
        """
        if value not in dict(Order.PAYMENT_METHOD_CHOICES).keys():
            raise serializers.ValidationError(f"Invalid payment method. Valid choices are: {', '.join(dict(Order.PAYMENT_METHOD_CHOICES).keys())}")
        return value

    def validate_shipping_address(self, value):
        """
        Ensure that a valid shipping address is provided.
        """
        if not value:
            raise serializers.ValidationError("Shipping address is required.")
        return value

    def validate_email(self, value):
        """
        Ensure that the email is in a valid format.
        """
        if not value:
            raise serializers.ValidationError("Email is required.")
        if "@" not in value:
            raise serializers.ValidationError("Email is not valid.")
        return value

    def validate_phone_number(self, value):
        """
        Ensure that the phone number is valid.
        """
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits long and contain only numbers.")
        return value

    def validate(self, attrs):
        """
        Additional custom validation logic if needed.
        """
        # Validate if billing address is provided if payment method requires it
        if attrs.get('payment_method') in ['Stripe', 'PayPal', 'Esewa'] and not attrs.get('billing_address'):
            raise serializers.ValidationError("Billing address is required for this payment method.")
        return attrs

    # Logic for handling the order process
    def create(self, validated_data):
        """
        Handle the order creation from cart_id, converting cart items into order items.
        Sets a tracking number, calculates total, updates stock, and sends confirmation.
        """ 
        cart = validated_data.pop('cart', None)
        shipping_cost = validated_data.get('shipping_cost', 0)
        tax = validated_data.get('tax', 0)
        discount = validated_data.get('discount', 0)
        if not cart:
            raise serializers.ValidationError("Cart ID is required to create an order.")
        cart = Cart.objects.prefetch_related('items__product').filter(id=cart.id).first()
        if not cart:
            raise serializers.ValidationError("Cart not found.")

        cart_items = cart.items.all()
        if not cart_items:
            raise serializers.ValidationError("No items in the cart.")

        # Calculate subtotal from cart
        subtotal = sum(item.subtotal() for item in cart_items)
        total = subtotal + shipping_cost + tax - discount

        # Add calculated fields to validated_data
        validated_data['subtotal'] = subtotal
        validated_data['total'] = total
        validated_data['tracking_number'] = self.generate_unique_tracking_number()
        validated_data['cart'] = cart

        # Create the order
        order = super().create(validated_data)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.new_price,
                discount=0,
            )

            item.product.quantity -= item.quantity
            item.product.save()

        # cart.items.update(is_deleted=True)
        self.send_order_confirmation_email(order)
        return order

    def generate_unique_tracking_number(self):
        """
        Generate a unique tracking number using a mix of uppercase letters and digits.
        Ensures no conflict with existing orders.
        """
        while True:
            tracking_number = get_random_string(length=12, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            if not Order.objects.filter(tracking_number=tracking_number).exists():
                return tracking_number

    def update_product_stock(self, products_data):
        """
        Reduce product stock when an order is placed.
        """
        for product_data in products_data:
            product = Product.objects.get(id=product_data['product_id'])
            if product.quantity >= product_data['quantity']:
                product.quantity -= product_data['quantity']
                product.save()
            else:
                raise ValidationError(f"Not enough stock for {product.title}.")

    def send_order_confirmation_email(self, order):
        """
        Send an order confirmation email after the order is created.
        """
        # Code to send the email goes here
        # This could be an email to the customer, admin, or both.
        pass

    def update(self, instance, validated_data):
        """
        Handle order updates, including updating stock and other order attributes.
        """
        # Before updating, handle stock if necessary (e.g., when a status change affects stock)
        if validated_data.get('order_status') == 'Cancelled' and instance.order_status != 'Cancelled':
            self.restore_stock(instance)

        # Perform regular update
        return super().update(instance, validated_data)

    def restore_stock(self, order):
        """
        Restore stock if an order is cancelled.
        """
        for order_item in order.order_items.all():
            product = order_item.product
            product.quantity += order_item.quantity
            product.save()



class OrderItemSerializer(BaseModelSerializer):
    order = OrderSerializer(read_only=True) 
    order_id = serializers.PrimaryKeyRelatedField(
        queryset = Order.objects.all(),
        source = 'order',
        write_only=True
    )
    product_id = serializers.PrimaryKeyRelatedField(
        queryset = Product.objects.all(),
        source = 'product',
        write_only=True
    )
    product = ProductSerializer(read_only=True)  
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'order','product_id','order_id' ,'product', 'quantity', 'price', 'discount', 'total', 'created_at', 'updated_at'
        ]

    def validate_quantity(self, value):
        """
        Ensures that the quantity is a positive number.
        """
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        return value

    def validate_price(self, value):
        """
        Ensures that the price is a positive value.
        """
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive value.")
        return value

    def validate_discount(self, value):
        """
        Ensures that the discount is not greater than the price.
        """
        if value > self.initial_data.get('price', 0):
            raise serializers.ValidationError("Discount cannot be greater than the price.")
        return value

    def create(self, validated_data):
        """
        Override create method to calculate the total of the OrderItem.
        """
        validated_data['total'] = (validated_data['price'] * validated_data['quantity']) - validated_data['discount']
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Override update method to recalculate total whenever the data is updated.
        """
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.price = validated_data.get('price', instance.price)
        instance.discount = validated_data.get('discount', instance.discount)
        instance.total = (instance.price * instance.quantity) - instance.discount
        instance.save()
        return instance
