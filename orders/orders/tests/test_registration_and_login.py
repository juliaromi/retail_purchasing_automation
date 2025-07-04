import pytest

from rest_framework.test import APIClient

from backend.serializers import UserRegistrationResponseSerializer


class TestRegistrationAndLogin:

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
