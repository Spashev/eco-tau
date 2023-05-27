from django.urls import reverse

from account import RoleType
from tests import BaseTestCase


class TestUsersCreate(BaseTestCase):
    def test_users_create(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('users-list')

        data = {
            "username": "user1",
            "email": "user1@example.com",
            "first_name": "user1",
            "last_name": "user1",
            "middle_name": "test",
            "phone_number": "8123471231",
            "password": "123",
            "role": "CLIENT"
        }
        response = self.client.post(url, data=data)

        assert response.status_code == 201
        assert response.data.get("id") == 1
        assert response.data.get("email") == "user1@example.com"
        assert response.data.get("role") == RoleType.CLIENT
