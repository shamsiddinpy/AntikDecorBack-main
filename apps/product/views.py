from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models import Filter, Product, BaseCategory, Category
from apps.product.pagination import DynamicPageNumberPagination
from apps.product.serializers import (
    FilterSerializer, ProductListSerializer, ProductSerializer, SidebarSerializer, CategorySerializer
)
from config.utils import get_by_category_id, get_by_filter_id, get_by_sidebar_id, get_by_search


class ProductListView(APIView):
    permission_classes = [AllowAny]
    pagination_class = DynamicPageNumberPagination
    category_id_param = openapi.Parameter(
        'category_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='(sub)category id')
    sidebar_id_param = openapi.Parameter(
        'sidebar_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='sidebar (sub)category id')
    page_param = openapi.Parameter(
        'page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='page number')
    search_param = openapi.Parameter(
        'search', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='searching')
    filter_param = openapi.Parameter(
        'filter_id', openapi.IN_QUERY, type=openapi.FORMAT_UUID, description='Filter product with custom filters')

    def get_queryset(self):
        queryset = Product.objects.all()
        queryset = get_by_category_id(self.request, queryset)
        queryset = get_by_sidebar_id(self.request, queryset)
        queryset = get_by_search(self.request, queryset)
        queryset = get_by_filter_id(self.request, queryset)
        return queryset.order_by('vendor_code')

    @swagger_auto_schema(
        manual_parameters=[
            category_id_param, sidebar_id_param, page_param, search_param, filter_param,
            openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description=('page_size2'))
        ],
        #  @swagger_auto_schema(
        #     manual_parameters=[category_id_param, sidebar_id_param, page_param, search_param, filter_param],
        #     responses={200: ProductListSerializer(many=True)},
        #     pagination_class=PageNumberPagination,
        #     tags=['Product'],
        # )
        responses={200: ProductListSerializer(many=True)},
        pagination_class=DynamicPageNumberPagination,
        tags=['Product'],
    )
    def get(self, request):
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProductListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: ProductSerializer()},
        tags=['Product'],
    )
    def get(self, request, product_id):
        instance = get_object_or_404(Product, id=product_id)
        serializer = ProductSerializer(instance, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class NewProductsView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: ProductListSerializer(many=True)},
        tags=['Product'],
    )
    def get(self, request):
        queryset = Product.new_products.all().order_by('-created')
        serializer = ProductListSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: CategorySerializer()},
        tags=['Category'],
    )
    def get(self, request, category_id):
        queryset = Category.objects.filter(is_top=True)
        category = get_object_or_404(queryset, id=category_id)
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class SidebarView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: SidebarSerializer()},
        tags=['Category'],
    )
    def get(self, request, category_id):
        queryset = BaseCategory.objects.filter(
            Q(is_top=True) | Q(parent__is_top=True)
        )
        category = get_object_or_404(queryset, id=category_id)
        serializer = SidebarSerializer(category, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class FilterList(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: SidebarSerializer(many=True)},
        tags=['Product'],
    )
    def get(self, request):
        filters = Filter.objects.all()
        serializer = FilterSerializer(filters, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
