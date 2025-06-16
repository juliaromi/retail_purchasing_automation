from pprint import pprint

import pytest

from rest_framework.test import APIClient

from backend.models import User, ProductInfo, Contact, DeliveryAddress
from backend.serializers import UserRegistrationResponseSerializer, ProductListSerializer, CertainProductSerializer, \
    CartContainsSerializer, DeliveryAddressSerializer, UserDeliveryDetailsSerializer


class TestProductAPI:

    @pytest.mark.django_db
    def test_register_customer(self, validate_response_dict):
        """
        Testing successful registration of new user
        """

        client = APIClient()
        data = {
            'first_name': 'Testname',
            'last_name': 'Testlastname',
            'login': 'test@test.com',
            'password': 'testpassword',
        }
        response = client.post('/register/', data=data)

        assert response.status_code == 201
        assert validate_response_dict(UserRegistrationResponseSerializer, response)

    @pytest.mark.django_db
    def test_login_user(self, test_user):
        """
        Testing successful login functionality
        """

        test_user()
        client = APIClient()
        data = {
            'username': 'test@test.com',
            'password': 'testpassword'
        }

        response = client.post('/login/', data=data)

        assert response.status_code == 200
        assert 'token' in response.data

    @pytest.mark.django_db
    def test_view_users_list_and_create_user_by_admin_user(self, test_admin_user,
                                                           validate_response_dict, validate_response_list):
        """
        The following test verifies that a user with administrator privileges can retrieve the list of users
        and successfully create a new user via the API
            """

        client = APIClient()
        client.force_authenticate(user=test_admin_user())
        response = client.get('/api/v1/users/')

        assert response.status_code == 200
        assert validate_response_list(UserRegistrationResponseSerializer, response)

        data = {
            'first_name': 'Testname',
            'last_name': 'Testlastname',
            'login': 'test@test.ru',
            'password': 'testpassword',
        }
        response = client.post('/api/v1/users/', data=data)

        assert response.status_code == 201
        assert validate_response_dict(UserRegistrationResponseSerializer, response)

    @pytest.mark.django_db
    def test_view_users_list_by_user_without_admin_privileges(self, test_user,
                                                              validate_response_dict, validate_response_list):
        """
        The following test verifies that a user without administrator privileges can't retrieve the list of users
        """

        client = APIClient()
        client.force_authenticate(user=test_user())
        response = client.get('/api/v1/users/')

        assert response.status_code == 403

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

    @pytest.mark.django_db
    def test_add_delivery_address(self, test_user, validate_response_dict):
        """
        Checks that an authenticated user can add delivery address
        """

        client = APIClient()
        client.force_authenticate(user=test_user())

        param = {
            "city": "Testcity",
            "street": "Teststreet",
            "building": 4
        }
        response = client.post('/api/v1/delivery-address/', data=param)
        assert response.status_code == 201
        assert validate_response_dict(DeliveryAddressSerializer, response)

    @pytest.mark.django_db
    def test_add_delivery_address_by_unauthenticated_user(self):
        """
        Checks that an unauthenticated user cannot add delivery address
        """

        client = APIClient()

        param = {
            "city": "Testcity",
            "street": "Teststreet",
            "building": 4
        }
        response = client.post('/api/v1/delivery-address/', data=param)
        assert response.status_code == 401

    @pytest.mark.django_db
    def test_update_user_delivery_address(self, test_user):
        """
        Checks that an authenticated user can update delivery address
        """

        client = APIClient()
        client.force_authenticate(user=test_user())

        param = {
            "city": "Testcity",
            "street": "Teststreet",
            "building": 4
        }
        response = client.post('/api/v1/delivery-address/', data=param)
        assert response.status_code == 201
        delivery_id = response.data.get('id')

        param = {
            "street": "Teststreetupdate"
        }
        response = client.patch(f'/api/v1/delivery-address/{delivery_id}/', data=param)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_delete_user_delivery_address(self, test_user):
        """
        Checks that an authenticated user can remove delivery address
        """

        client = APIClient()
        client.force_authenticate(user=test_user())

        param = {
            "city": "Testcity",
            "street": "Teststreet",
            "building": 4
        }

        response = client.post('/api/v1/delivery-address/', data=param)
        assert response.status_code == 201
        delivery_id = response.data.get('id')

        response = client.delete(f'/api/v1/delivery-address/{delivery_id}/')
        assert response.status_code == 204

    @pytest.mark.django_db
    def test_add_user_contact(self, test_user):
        """
        Checks that an authenticated user can add contacts for receiving statuses and notifications
        """

        client = APIClient()
        client.force_authenticate(user=test_user())

        param = {
            "type": "PHONE",
            "value": "89999999999"
        }
        response = client.post('/api/v1/contacts/', data=param)

        assert response.status_code == 201
        assert response.data.get('type') == 'PHONE'
        assert response.data.get('value') == '89999999999'


    @pytest.mark.django_db
    def test_add_user_contact_by_unauthenticated_user(self):
        """
        Checks that an unauthenticated user cannot add contacts for receiving statuses and notifications
        """

        client = APIClient()
        param = {
            "type": "PHONE",
            "value": "89999999999"
        }
        response = client.post('/api/v1/contacts/', data=param)

        assert response.status_code == 401

    @pytest.mark.django_db
    def test_change_user_contact(self, test_user):
        """
        Checks that an authenticated user can change contacts for receiving statuses and notifications
        """

        client = APIClient()
        client.force_authenticate(user=test_user())

        param = {
            "type": "PHONE",
            "value": "89999999999"
        }
        response = client.post('/api/v1/contacts/', data=param)
        assert response.status_code == 201
        contact_id = response.data.get('id')

        param = {
            "type": "PHONE",
            "value": "89999999900"
        }
        response = client.patch(f'/api/v1/contacts/{contact_id}/', data=param)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_delete_user_contact(self, test_user):
        """
        Checks that an authenticated user can remove contacts for receiving statuses and notifications
        """

        client = APIClient()
        client.force_authenticate(user=test_user())

        param = {
            "type": "PHONE",
            "value": "89999999999"
        }
        response = client.post('/api/v1/contacts/', data=param)
        assert response.status_code == 201
        contact_id = response.data.get('id')

        response = client.delete(f'/api/v1/contacts/{contact_id}/')
        assert response.status_code == 204

    @pytest.mark.django_db
    def test_view_user_delivery_details(self, test_user, test_admin_user, validate_response_list):
        """
        Tests that an admin user can retrieve delivery details - contacts and addresses, of all users.
        """

        test_user = test_user()

        Contact.objects.create(
            user=test_user,
            type="PHONE",
            value="89999999999"
        )

        DeliveryAddress.objects.create(
            user=test_user,
            city="Testcity",
            street="Teststreet",
            building=1
        )

        client = APIClient()
        client.force_authenticate(user=test_admin_user())

        response = client.get('/api/v1/user-delivery-details/')
        assert response.status_code == 200
        assert validate_response_list(UserDeliveryDetailsSerializer, response)
