import pytest
from rest_framework.exceptions import ValidationError


@pytest.fixture
def validate_response():
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
