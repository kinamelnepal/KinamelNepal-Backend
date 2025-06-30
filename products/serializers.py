from rest_framework import serializers

from categories.models import Category
from categories.serializers import CategorySerializer
from core.serializers import BaseModelSerializer

from .models import Product
from .utils.currency import CURRENCY_TO_SYMBOL_MAPPING, get_exchange_rate


class ProductSerializer(BaseModelSerializer):
    category = CategorySerializer(many=False, read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    new_price = serializers.SerializerMethodField()
    old_price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    currency_symbol = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "uuid",
            "category",
            "category_id",
            "sale",
            "image",
            "image_two",
            "new_price",
            "old_price",
            "new_price",
            "old_price",
            "currency",
            "currency_symbol",
            "weight",
            "quantity",
            "description",
            "short_description",
            "dimensions",
            "title",
            "rating",
            "status",
            "location",
            "brand",
            "sku",
            "slug",
            "created_at",
            "updated_at",
        ]

    def get_currency(self, obj):
        return self.context.get("currency", "NPR")

    def get_new_price(self, obj):
        currency = self.context.get("currency", "NPR").upper()
        rate = get_exchange_rate(currency)
        print(rate, "the rate")
        return round(float(obj.new_price) * rate, 2) if obj.new_price else None

    def get_old_price(self, obj):
        currency = self.context.get("currency", "NPR").upper()
        rate = get_exchange_rate(currency)

        return round(float(obj.old_price) * rate, 2) if obj.old_price else None

    def get_currency_symbol(self, obj):
        currency = self.context.get("currency", "NPR").upper()
        return CURRENCY_TO_SYMBOL_MAPPING.get(currency, "Rs")
