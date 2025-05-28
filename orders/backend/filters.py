import django_filters

from backend.models import ProductParameter


class ProductListFilter(django_filters.FilterSet):
    price_from = django_filters.NumberFilter(field_name='product_info__price', lookup_expr='gte')
    price_to = django_filters.NumberFilter(field_name='product_info__price', lookup_expr='lte')
    shop = django_filters.CharFilter(field_name='product_info__shop__name', lookup_expr='icontains')
    model = django_filters.CharFilter(field_name='product_info__model__name', lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='product_info__model__category__name', lookup_expr='icontains')
    parameter = django_filters.CharFilter(field_name='parameter__name', lookup_expr='icontains')
    value_from = django_filters.NumberFilter(field_name='value', lookup_expr='gte')
    value_to = django_filters.NumberFilter(field_name='value', lookup_expr='lte')

    class Meta:
        model = ProductParameter
        fields = ['price_from', 'price_to', 'shop', 'model', 'category', 'parameter', 'value_from', 'value_to']
