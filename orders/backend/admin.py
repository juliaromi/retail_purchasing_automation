from django.contrib import admin

from .models import (User, Shop, Category, Model, ProductInfo,
                     Parameter, ProductParameter, Order, OrderItem, Contact, DeliveryAddress)


class CategoryInline(admin.TabularInline):
    model = Category.shops.through


class ShopAdmin(admin.ModelAdmin):
    inlines = [
        CategoryInline,
    ]
    list_display = ('name', 'site',)
    exclude = ('product_categories',)


class ModelAdmin(admin.ModelAdmin):
    inlines = [
        CategoryInline,
    ]


class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'model', 'shop', 'quantity', 'price', 'rrp',)


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ('product_info', 'parameter', 'value', )


from django import forms
from django.contrib import admin

class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = None

        if self.instance and self.instance.pk:
            user = self.instance.user
        else:
            data = self.data or {}
            user_id = data.get('user') or data.get('user_id')
            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                except User.DoesNotExist:
                    user = None

        if user:
            self.fields['delivery_address'].queryset = DeliveryAddress.objects.filter(user=user)
        else:
            self.fields['delivery_address'].queryset = DeliveryAddress.objects.none()


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = ('user', 'created_at', 'status', 'order_total', )


@admin.register(OrderItem)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'shop', 'quantity', )


class ContactAdmin(admin.TabularInline):
    model = Contact


class DeliveryAddressAdmin(admin.TabularInline):
    model = DeliveryAddress


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('login', 'first_name', 'middle_name', 'last_name', 'is_staff', 'is_superuser', 'created_at',)
    inlines = [
        ContactAdmin,
        DeliveryAddressAdmin,
    ]


admin.site.register(Shop, ShopAdmin)
admin.site.register(Category)
admin.site.register(Model)
admin.site.register(ProductInfo, ProductInfoAdmin)
admin.site.register(Parameter)
