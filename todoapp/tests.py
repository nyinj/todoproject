from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class TaskAPITestCase(APITestCase):
    def setUp(self):
        # create a user
        self.user = User.objects.create_user(username='testuser', password='password123')
        # URL for token
        self.token_url = reverse('token_obtain_pair')
        # URL for tasks list
        self.tasks_url = reverse('task-list')  # make sure your view has name='task-list'

    def test_obtain_jwt_token(self):
        response = self.client.post(self.token_url, {'username': 'testuser', 'password': 'password123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_task_list_requires_auth(self):
        response = self.client.get(self.tasks_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_task_list_authenticated(self):
        # get token first
        response = self.client.post(self.token_url, {'username': 'testuser', 'password': 'password123'}, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.tasks_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
