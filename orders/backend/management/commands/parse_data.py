import os

from django.core.management.base import BaseCommand
from yaml import load, Loader

from ...models import Shop, Category


class Command(BaseCommand):
    help = 'Data parser'

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'shop1.yaml')

        with open(file_path, encoding='utf-8') as file:
            data: dict = load(file, Loader=Loader)

            shop_name = data.get('shop')
            shop = Shop.objects.create(name=shop_name)
            print(f'Shop {shop} uploaded')

            categories = data.get('categories')
            for category in categories:
                product_category = Category.objects.create(id=category.get('id'), name=category.get('name'))
                product_category.shops.add(shop)
                print(f'Category {category.get("name")} uploaded')
