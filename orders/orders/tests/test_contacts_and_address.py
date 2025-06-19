import pytest

from rest_framework.test import APIClient

from backend.models import Contact, DeliveryAddress
from backend.serializers import DeliveryAddressSerializer, UserDeliveryDetailsSerializer


class TestUserContactsAndAddress:

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
