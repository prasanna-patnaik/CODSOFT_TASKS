from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthenticationAPITests(APITestCase):
    def test_user_can_register_and_receive_tokens(self):
        response = self.client.post(
            reverse("auth-register"),
            {
                "username": "jane",
                "email": "jane@example.com",
                "first_name": "Jane",
                "last_name": "Doe",
                "password": "VeryStrongPass123!",
                "password_confirm": "VeryStrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "User registered successfully.")
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertTrue(User.objects.filter(username="jane").exists())

    def test_user_can_login_and_read_current_user(self):
        User.objects.create_user(
            username="jane",
            email="jane@example.com",
            password="VeryStrongPass123!",
        )

        login_response = self.client.post(
            reverse("auth-login"),
            {"username": "jane", "password": "VeryStrongPass123!"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        access_token = login_response.data["tokens"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        me_response = self.client.get(reverse("auth-me"))
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["username"], "jane")

    def test_current_user_requires_authentication(self):
        response = self.client.get(reverse("auth-me"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
