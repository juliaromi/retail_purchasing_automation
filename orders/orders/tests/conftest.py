import pytest
from django.core.management import call_command
from rest_framework.exceptions import ValidationError

from backend.management.commands.parse_data import Command
from backend.models import User


@pytest.fixture
def validate_response_dict():
    """
    Fixture that returns a function for validating response data.
    If validation fails, the test will fail with a message.
    """

    def wrapper(serializer_class, response):
        serializer = serializer_class(data=response.json())
        try:
            serializer.is_valid(raise_exception=True)
            return True
        except ValidationError as e:
            pytest.fail(f'Invalid response data: {e}')

    return wrapper


@pytest.fixture
def validate_response_list():
    """
    Fixture that returns a function for validating response data.
    If validation fails, the test will fail with a message.
    """

    def wrapper(serializer_class, response):
        serializer = serializer_class(data=response.json(), many=True)
        try:
            serializer.is_valid(raise_exception=True)
            return True
        except ValidationError as e:
            pytest.fail(f'Invalid response data: {e}')

    return wrapper


@pytest.fixture
def load_test_data(django_db_blocker):
    """
    Fixture that flushes the database
    and loads initial test data using a custom management command
    """

    with django_db_blocker.unblock():
        call_command('flush', '--noinput')
        cmd = Command()
        cmd.handle()
    yield

@pytest.fixture
def test_user():
    """
    Fixture that creates and returns a test user without administrator privileges instance
    """

    def wrapper():
        test_user = User.objects.create_user(
            first_name='Testname',
            last_name='Testlastname',
            login='test@test.com',
            password='testpassword',
        )
        return test_user
    return wrapper

@pytest.fixture
def test_admin_user():
    """
    Fixture that creates and returns a test user with administrator privileges instance
    """

    def wrapper():
        test_admin_user = User.objects.create_user(
            first_name='Testname',
            last_name='Testlastname',
            login='admin@test.com',
            password='testpassword',
            is_staff=True
        )
        return test_admin_user
    return wrapper
