from django.urls import reverse

from account import RoleType
from tests import BaseTestCase


class TestUsersCreate(BaseTestCase):
    def test_users_create(self):
        self.api_client.force_authenticate(user=self.admin)
        url = reverse('users-create-lists')

        data = {
          "email": "user@example.com",
          "first_name": "string",
          "last_name": "string",
          "middle_name": "string",
          "phone_number": "string",
          "date_of_birth": "2023-10-29",
          "password": "string",
          "role": "CLIENT"
        }

        response = self.api_client.post(url, data=data)

        assert response.status_code == 201
        assert response.data.get("id") == 1
        assert response.data.get("email") == "user1@example.com"
        assert response.data.get("role") == RoleType.CLIENT
