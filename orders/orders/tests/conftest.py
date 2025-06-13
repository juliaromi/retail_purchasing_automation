import pytest
from django.core.management import call_command
from rest_framework.exceptions import ValidationError

from backend.management.commands.parse_data import Command


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
    with django_db_blocker.unblock():
        call_command('flush', '--noinput')
        cmd = Command()
        cmd.handle()
    yield

