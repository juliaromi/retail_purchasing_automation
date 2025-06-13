import django_filters

from backend.models import ProductParameter


class ProductListFilter(django_filters.FilterSet):
    """
    FilterSet for ProductParameter model
    """

    price_from = django_filters.NumberFilter(field_name='product_info__price', lookup_expr='gte')
    price_to = django_filters.NumberFilter(field_name='product_info__price', lookup_expr='lte')
    shop = django_filters.CharFilter(field_name='product_info__shop__name', lookup_expr='icontains')
    model = django_filters.CharFilter(field_name='product_info__model__name', lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='product_info__model__category__name', lookup_expr='icontains')
    parameter_name = django_filters.CharFilter(field_name='parameter__name', lookup_expr='icontains')
    parameter_value = django_filters.CharFilter(field_name='parameter__name', lookup_expr='icontains')

    class Meta:
        model = ProductParameter
        fields = ['price_from', 'price_to', 'shop', 'model', 'category', 'parameter_name', 'parameter_value', ]

    def filter_queryset(self, queryset):
        if 'parameter_name' in self.data and 'parameter_value' in self.data:
            return queryset.filter(
                parameter__name=self.data.get('parameter_name'),
                value=self.data.get('parameter_value')
            )
        return super().filter_queryset(queryset)
