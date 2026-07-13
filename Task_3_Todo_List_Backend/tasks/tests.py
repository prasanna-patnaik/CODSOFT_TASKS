from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from tasks.models import Task


User = get_user_model()


def access_token_for(user):
    return str(RefreshToken.for_user(user).access_token)


class TaskAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jane",
            email="jane@example.com",
            password="VeryStrongPass123!",
        )
        self.other_user = User.objects.create_user(
            username="alex",
            email="alex@example.com",
            password="VeryStrongPass123!",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token_for(self.user)}")

    def test_anonymous_users_cannot_access_tasks(self):
        self.client.credentials()

        response = self.client.get(reverse("task-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_create_only_their_own_task(self):
        response = self.client.post(
            reverse("task-list"),
            {
                "title": "Finish backend project",
                "description": "Complete review.",
                "completed": False,
                "priority": "high",
                "category": "work",
                "due_date": (timezone.now() + timedelta(days=1)).isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=response.data["id"])
        self.assertEqual(task.owner, self.user)

    def test_user_reads_only_owned_tasks(self):
        own_task = Task.objects.create(title="Mine", owner=self.user)
        Task.objects.create(title="Not mine", owner=self.other_user)

        response = self.client.get(reverse("task-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task_ids = [task["id"] for task in response.data["results"]]
        self.assertEqual(task_ids, [own_task.id])

    def test_user_cannot_retrieve_update_or_delete_another_users_task(self):
        task = Task.objects.create(title="Private", owner=self.other_user)
        detail_url = reverse("task-detail", args=[task.id])

        retrieve_response = self.client.get(detail_url)
        update_response = self.client.patch(detail_url, {"completed": True}, format="json")
        delete_response = self.client.delete(detail_url)

        self.assertEqual(retrieve_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(update_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(delete_response.status_code, status.HTTP_404_NOT_FOUND)
        task.refresh_from_db()
        self.assertFalse(task.completed)

    def test_filter_search_order_and_pagination_are_available(self):
        Task.objects.create(
            title="Backend review",
            description="Production readiness",
            completed=False,
            priority=Task.Priority.HIGH,
            category="work",
            owner=self.user,
        )
        Task.objects.create(
            title="Buy groceries",
            completed=False,
            priority=Task.Priority.LOW,
            category="personal",
            owner=self.user,
        )

        response = self.client.get(
            reverse("task-list"),
            {
                "completed": "false",
                "priority": "high",
                "category": "work",
                "search": "backend",
                "ordering": "-created_at",
                "page": 1,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Backend review")
