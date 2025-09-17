from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer


# ---------------- JWT Token ----------------


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# ---------------- Product CRUD ----------------
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    lookup_field = 'slug'  # ✅ Lookup products by slug instead of id

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.query_params.get('category')
        is_deal = self.request.query_params.get('is_deal')
        queryset = Product.objects.all()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if is_deal:
            queryset = queryset.filter(is_deal=True)
        return queryset
    
    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        products = self.get_queryset()
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        products = self.get_queryset()
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        products = self.get_queryset()
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ---------------- Category CRUD ----------------
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    # GET /api/categories/with_products/
    @action(detail=False, methods=['get'])
    def with_products(self, request):
        categories = Category.objects.prefetch_related('products').all()
        data = []
        for category in categories:
            products = category.products.all()
            if products.exists():
                data.append({
                    'id': category.id,
                    'name': category.name,
                    'slug': category.slug,
                    'icon': category.icon.url if category.icon else None,  # ✅ Safe icon URL
                    'products': ProductSerializer(products, many=True).data
                })
        return Response(data)

    # GET /api/categories/products_by_category/
    @action(detail=False, methods=['get'])
    def products_by_category(self, request):
        categories = Category.objects.prefetch_related('products').all()
        grouped_data = [
            {
                'category': category.name,
                'slug': category.slug,
                'products': ProductSerializer(category.products.all(), many=True).data
            }
            for category in categories if category.products.exists()
        ]
        return Response(grouped_data)


# ---------------- Read-only APIs ----------------
class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'  # ✅ Match React route /product/:slug


class ProductsByCategory(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        category_slug = self.kwargs.get('slug')
        return Product.objects.filter(category__slug=category_slug)
