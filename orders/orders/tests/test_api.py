import pytest

from rest_framework.test import APIClient

from backend.models import User
from backend.serializers import UserRegistrationResponseSerializer


@pytest.mark.django_db
def test_register_customer(validate_response):
    """
    Testing successful registration of new user.
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
    assert validate_response(UserRegistrationResponseSerializer, response) == True

    test_user = User.objects.get(login='test@test.com')
    test_user.delete()
