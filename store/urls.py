from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .views import ProductViewSet, CategoryViewSet

# Router setup
router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('categories', CategoryViewSet)

urlpatterns = [
    # All CRUD endpoints from router
    path('', include(router.urls)),

    # JWT Authentication
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Extra read-only category filter
    path('category/<slug:slug>/', views.ProductsByCategory.as_view(), name='products-by-category'),
]
