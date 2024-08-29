from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from texnomart.models import Category, Product, Key, Value
from texnomart.serializers import CategorySerializer, ProductModelSerializer, ProductSerializer, AttributeSerializer, \
    KeySerializer, ValueSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from texnomart.permissions import IsSuperAdminOrReadOnly


class AllProductsView(ListAPIView):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', ]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    authentication_classes = [JWTAuthentication, TokenAuthentication]



class CategoryListAPI(generics.ListAPIView):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', ]
    authentication_classes = [JWTAuthentication, TokenAuthentication]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CreateCategoryView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class UpdateCategoryView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get(self, request, *args, **kwargs):
        slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=slug)
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=slug)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteCategoryView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSuperAdminOrReadOnly]
    lookup_field = 'slug'

    def get(self, request, *args, **kwargs):
        slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=slug)
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #
    def delete(self, request, *args, **kwargs):
        slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=slug)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductListAPI(ListAPIView):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', ]
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        queryset = Product.objects.filter(category__slug=category_slug)
        return queryset


class ProductDetailView(RetrieveAPIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]
    serializer_class = ProductModelSerializer
    queryset = Product.objects.all()
    lookup_field = 'id'


class ProductDeleteView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        data = Product.objects.get(id=self.kwargs['pk'])
        if data:
            serializer = ProductSerializer(data, context={'request': request})
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        data = Product.objects.get(id=self.kwargs['pk'])
        data.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductUpdateView(RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def delete(self, request, *args, **kwargs):
        data = Product.objects.get(id=self.kwargs['pk'])
        data.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ProductAttribute(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('group').prefetch_related('attributes__key', 'attributes__value')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filter_fields = ['created_at']
    search_fields = ['name', ]
    serializer_class = AttributeSerializer
    lookup_field = 'slug'


class AttributeKeyListAPI(generics.ListAPIView):
    queryset = Key.objects.all()
    serializer_class = KeySerializer


class AttributeValueListAPI(generics.ListAPIView):
    queryset = Value.objects.all()
    serializer_class = ValueSerializer
