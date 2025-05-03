import os

from django.core.management.base import BaseCommand
from yaml import load, Loader

from ...models import Shop, Category, Model, ProductInfo, Parameter, ProductParameter


class Command(BaseCommand):
    help = 'Data parser'

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'shop1.yaml')

        with open(file_path, encoding='utf-8') as file:
            data: dict = load(file, Loader=Loader)

            #Loading store data
            shop_name: dict = data.get('shop')
            shop = Shop.objects.create(name=shop_name)
            print(f'Shop {shop} uploaded')

            #Loading product category data
            categories = data.get('categories')
            categories_dict = {}
            for category in categories:
                product_category = Category.objects.create(id=category.get('id'), name=category.get('name'))
                product_category.shops.add(shop)
                categories_dict[category.get('id')] = product_category
                print(f'Category {category.get("name")} uploaded')

            # Loading product model data
            goods = data.get('goods')
            models_dict = {}
            for good in goods:
                if good.get('model') not in models_dict.keys():
                    category_id = good.get('category')
                    category_object = categories_dict.get(category_id)
                    product_model = Model.objects.create(name=good.get('model'), category=category_object)
                    models_dict[good.get('model')] = product_model
                    print(f'Model {good.get("model")} uploaded')

            # Loading product information data
            products_info_dict = {}
            for good in goods:
                model_name = good.get('model')
                model_object = models_dict.get(model_name)
                product_info_model = ProductInfo.objects.create(
                    id=good.get('id'),
                    product_name=good.get('name'),
                    model=model_object,
                    shop=shop,
                    quantity=good.get('quantity'),
                    price=good.get('price'),
                    rrp=good.get('price_rrc'),
                )
                products_info_dict[good.get('id')] = product_info_model
                print(f'Product {good.get("name")} uploaded')

            # Loading product parameters names
            for good in goods:
                parameters = good.get('parameters')
                for parameter in parameters.keys():
                    parameter_object, created = Parameter.objects.get_or_create(name=parameter)
                    print(f'Parameter {parameter} uploaded')

            # Loading product parameters data
            for good in goods:
                good_id = good.get('id')
                product_info_object = products_info_dict.get(good_id)
                parameters = good.get('parameters')
                for key, value in parameters.items():
                    parameter_object = Parameter.objects.get(name=key)
                    product_parameter_object, created = ProductParameter.objects.get_or_create(
                        product_info=product_info_object,
                        parameter=parameter_object,
                        value=value,
                    )
                    print(f"Parameter's info {key}: {value} uploaded")
