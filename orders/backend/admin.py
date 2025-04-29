from django.contrib import admin

from .models import (User, Shop, Category, Model, ProductInfo,
                     Parameter, ProductParameter, Order, OrderItem, Contact)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('login', 'name', 'lastname', 'is_staff', 'is_superuser', 'created_at',)


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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'status', 'order_total', )


@admin.register(OrderItem)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'shop', 'quantity', )


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('type', 'user', 'value',)


admin.site.register(Shop, ShopAdmin)
admin.site.register(Category)
admin.site.register(Model)
admin.site.register(ProductInfo, ProductInfoAdmin)
admin.site.register(Parameter)
