import pytest
from django.core.cache import cache

from rest_framework.test import APIClient

class TestThrottle:

    @pytest.mark.django_db
    def test_anon_user_throttling(self):
        """
        Verify that anon user's requests are throttled after exceeding the allowed rate.
        """

        cache.clear()
        client = APIClient()

        for i in range(5):
            response = client.get('/api/v1/product-list/')
            assert response.status_code == 200

        response = client.get('/api/v1/product-list/')
        assert response.status_code == 429

    @pytest.mark.django_db
    def test_authenticated_user_throttling(self, test_user):
        """
        Verify that authenticated user's requests are throttled after exceeding the allowed rate.
        """

        cache.clear()
        client = APIClient()
        client.force_authenticate(user=test_user())

        for i in range(20):
            response = client.get('/api/v1/product-list/')
            assert response.status_code == 200

        response = client.get('/api/v1/product-list/')
        assert response.status_code == 429
