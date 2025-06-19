import pytest

from rest_framework.test import APIClient

from backend.serializers import ProductListSerializer, CertainProductSerializer


class TestProductListAndProductInfo:

    @pytest.mark.django_db
    def test_view_product_list(self, load_test_data, validate_response_list):
        """
        The following test verifies that any store visitor can view the product list regardless of authorization
        """

        client = APIClient()
        response = client.get('/api/v1/product-list/')

        assert response.status_code == 200
        assert validate_response_list(ProductListSerializer, response)

    @pytest.mark.django_db
    def test_view_certain_product(self, load_test_data, validate_response_dict):
        """
        The following test verifies that any store visitor can view the certain product by id regardless of authorization
        """

        client = APIClient()
        response = client.get('/api/v1/product-list/1234568/')

        assert response.status_code == 200
        assert validate_response_dict(CertainProductSerializer, response)
        assert response.json().get('product_name') == 'Smartphone Samsung Galaxy Note20 256GB (mystic bronze)'

    @pytest.mark.django_db
    def test_view_product_list_with_filter_through_search(self, load_test_data, validate_response_list):
        """
        The following test verifies
        that any store visitor can view the product list with filter option regardless of authorization
        """

        client = APIClient()
        param = {
            "parameter_name": "Цвет",
            "parameter_value": "золотистый"
        }
        response = client.get('/api/v1/product-list/', data=param)

        assert response.status_code == 200
        assert validate_response_list(ProductListSerializer, response)
        assert response.json()[0].get('parameter') == {'Цвет': 'золотистый'}

    @pytest.mark.django_db
    def test_view_product_list_through_search(self, load_test_data, validate_response_list):
        """
        The following test verifies
        that any store visitor can search and view the product list regardless of authorization
        """

        client = APIClient()
        param = {
            "search": "Смартфоны"
        }
        response = client.get('/api/v1/product-list/', data=param)

        assert response.status_code == 200
        assert validate_response_list(ProductListSerializer, response)
        for item in response.json():
            assert item.get('category') == 'Смартфоны'
