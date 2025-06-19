import pytest

from rest_framework.test import APIClient

from backend.models import Contact, DeliveryAddress, ProductInfo, Order
from backend.serializers import OrderSerializer, OrderHistorySerializer


class TestProductAPIOrderManipulations:

    @pytest.mark.django_db
    def test_get_info_about_user_order(self, test_user, load_test_data, validate_response_dict):
        """
        Test retrieving the current user's active order (cart)
        """

        test_user = test_user()

        Contact.objects.create(
            user=test_user,
            type="EMAIL",
            value="test@test.com"
        )

        client = APIClient()
        client.force_authenticate(user=test_user)

        response = client.get('/api/v1/orders/user-cart/')
        assert response.status_code == 404

        product = ProductInfo.objects.first()

        param = {
            "product": product.id,
            "quantity": 2
        }
        response = client.post('/api/v1/cart-contains/', data=param)
        try:
            if response.status_code != 201:
                raise Exception('Product was not added to user\'s cart')
        except Exception as e:
            print(f'Error: {e}')

        response = client.get('/api/v1/orders/user-cart/')
        assert response.status_code == 200
        assert validate_response_dict(OrderSerializer, response)

    @pytest.mark.django_db
    def test_confirm_order(self, test_user, load_test_data):
        """
        Order confirmation test
        """

        test_user = test_user()

        contact = Contact.objects.create(
            user=test_user,
            type="EMAIL",
            value="test@test.com"
        )

        delivery_address = DeliveryAddress.objects.create(
            user=test_user,
            city="Testcity",
            street="Teststreet",
            building=1
        )

        client = APIClient()
        client.force_authenticate(user=test_user)

        product = ProductInfo.objects.first()

        param = {
            "product": product.id,
            "quantity": 2
        }
        response = client.post('/api/v1/cart-contains/', data=param)
        try:
            if response.status_code != 201:
                raise Exception('Product was not added to user\'s cart')
        except Exception as e:
            print(f'Error: {e}')

        order = Order.objects.filter(user=test_user, status=Order.OrderStatus.CREATED).first()

        order.delivery_address = delivery_address
        order.save()

        data = {
            "contact_id": contact.id,
            "order_id": order.id
        }

        response = client.post('/api/v1/order-confirmation/confirm-order/', data=data)
        assert response.status_code == 200
        assert response.data.get('message') == 'Order confirmed'

    @pytest.mark.django_db
    def test_view_order_history(self, test_user, load_test_data, validate_response_list):
        """
        Test that user can view their order history
        """

        test_user = test_user()

        contact = Contact.objects.create(
            user=test_user,
            type="EMAIL",
            value="test@test.com"
        )

        delivery_address = DeliveryAddress.objects.create(
            user=test_user,
            city="Testcity",
            street="Teststreet",
            building=1
        )

        client = APIClient()
        client.force_authenticate(user=test_user)

        product = ProductInfo.objects.first()

        param = {
            "product": product.id,
            "quantity": 2
        }
        response = client.post('/api/v1/cart-contains/', data=param)
        try:
            if response.status_code != 201:
                raise Exception('Product was not added to user\'s cart')
        except Exception as e:
            print(f'Error: {e}')

        order = Order.objects.filter(user=test_user, status=Order.OrderStatus.CREATED).first()

        order.delivery_address = delivery_address
        order.save()

        data = {
            "contact_id": contact.id,
            "order_id": order.id
        }

        response = client.post('/api/v1/order-confirmation/confirm-order/', data=data)
        try:
            if response.status_code != 200:
                raise Exception('Product was not confirmed')
        except Exception as e:
            print(f'Error: {e}')

        product = ProductInfo.objects.all()[1]

        param = {
            "product": product.id,
            "quantity": 1
        }
        response = client.post('/api/v1/cart-contains/', data=param)
        try:
            if response.status_code != 201:
                raise Exception('Product was not added to user\'s cart')
        except Exception as e:
            print(f'Error: {e}')

        response = client.get('/api/v1/orders/history/')
        assert response.status_code == 200
        assert validate_response_list(OrderHistorySerializer, response)
