from rest_framework import serializers
from .models import Category, Product
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["is_staff"] = user.is_staff
        token["is_superuser"] = user.is_superuser
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            "username": self.user.username,
            "is_staff": self.user.is_staff,
            "is_superuser": self.user.is_superuser,
        })
        return data


# ---------------- Category Serializer ----------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "icon"]
        read_only_fields = ["slug"]


# ---------------- Product Serializer ----------------
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)   # for GET
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True
    )  # for POST/PUT

    discounted_price = serializers.SerializerMethodField()
    on_sale = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "brand",
            "category", "category_id",   # ✅ both
            "description", "price", "is_deal", "discount_percent",
            "image", "discounted_price", "on_sale"
        ]
        read_only_fields = ["slug", "discounted_price", "on_sale"]

    def get_discounted_price(self, obj):
        return obj.discounted_price()

    def get_on_sale(self, obj):
        return bool(obj.discount_percent and obj.discount_percent > 0)

    # ✅ Fix create
    def create(self, validated_data):
        category = validated_data.pop("category_id")
        product = Product.objects.create(category=category, **validated_data)
        return product

    # ✅ Fix update
    def update(self, instance, validated_data):
        category = validated_data.pop("category_id", None)
        if category:
            instance.category = category
        return super().update(instance, validated_data)
