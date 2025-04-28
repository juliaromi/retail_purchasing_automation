from django.contrib import admin

from .models import User, Shop, Category, Model, ProductInfo, Parameter


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


admin.site.register(Shop, ShopAdmin)
admin.site.register(Category)
admin.site.register(Model)
admin.site.register(ProductInfo, ProductInfoAdmin)
admin.site.register(Parameter)
