import pytest

from rest_framework.test import APIClient

from backend.models import ProductInfo
from backend.serializers import CartContainsSerializer


class TestShoppingCart:

    @pytest.mark.django_db
    def test_add_product_to_cart(self, test_user, load_test_data, validate_response_dict):
        """
        Checks that an authenticated user can add a product to the cart and receive a valid response
        """

        client = APIClient()
        client.force_authenticate(user=test_user())
        product = ProductInfo.objects.first()

        param = {
            "product": product.id
        }
        response = client.post('/api/v1/cart-contains/', data=param)

        assert response.status_code == 201
        assert validate_response_dict(CartContainsSerializer, response)
        assert response.json().get('name') == product.product_name
        assert response.json().get('quantity') == 1

    @pytest.mark.django_db
    def test_unauthenticated_user_cannot_add_product_to_cart(self, load_test_data, validate_response_dict):
        """
        Checks that an unauthenticated user cannot add a product to the cart and receive a valid response
        """

        client = APIClient()
        product = ProductInfo.objects.first()

        param = {
            "product": product.id
        }
        response = client.post('/api/v1/cart-contains/', data=param)

        assert response.status_code == 401
        assert response.json().get('detail') == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_increase_product_quantity_in_cart(self, test_user, load_test_data, validate_response_dict):
        """
        Checks that an authenticated user can increase product quantity in the cart and receive a valid response
        """

        client = APIClient()
        client.force_authenticate(user=test_user())
        product = ProductInfo.objects.first()

        param = {
            "product": product.id,
            "quantity": 2
        }
        response = client.post('/api/v1/cart-contains/', data=param)
        assert response.status_code == 201
        assert response.json().get('quantity') == 2

        order_item_id = response.json().get('id')
        param = {
            "amount": 1
        }
        response = client.patch(f'/api/v1/cart-contains/{order_item_id}/increase/', data=param)

        assert response.status_code == 200
        assert validate_response_dict(CartContainsSerializer, response)
        assert response.json().get('name') == product.product_name
        assert response.json().get('quantity') == 3

    @pytest.mark.django_db
    def test_decrease_product_quantity_in_cart(self, test_user, load_test_data, validate_response_dict):
        """
        Checks that an authenticated user can decrease product quantity in the cart and receive a valid response
        """

        client = APIClient()
        client.force_authenticate(user=test_user())
        product = ProductInfo.objects.first()

        param = {
            "product": product.id,
            "quantity": 2
        }
        response = client.post('/api/v1/cart-contains/', data=param)
        assert response.status_code == 201
        assert response.json().get('quantity') == 2

        order_item_id = response.json().get('id')
        param = {
            "amount": 1
        }
        response = client.patch(f'/api/v1/cart-contains/{order_item_id}/decrease/', data=param)

        assert response.status_code == 200
        assert validate_response_dict(CartContainsSerializer, response)
        assert response.json().get('name') == product.product_name
        assert response.json().get('quantity') == 1

    @pytest.mark.django_db
    def test_remove_product_from_cart(self, test_user, load_test_data):
        """
        Checks that an authenticated user can remove product from the cart
        """

        client = APIClient()
        client.force_authenticate(user=test_user())
        product = ProductInfo.objects.first()

        param = {
            "product": product.id,
            "quantity": 3
        }
        response = client.post('/api/v1/cart-contains/', data=param)
        assert response.status_code == 201
        assert response.json().get('quantity') == 3

        order_item_id = response.json().get('id')
        response = client.delete(f'/api/v1/cart-contains/{order_item_id}/')

        assert response.status_code == 204
