from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from todoapp.models import Task  # Replace with your actual model if different


class TodoAPITest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Obtain JWT token
        url = reverse('token_obtain_pair')  # Must match your urls.py
        response = self.client.post(url, {'username': 'testuser', 'password': 'testpass'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data['access']
        
        # Set Authorization header for all future requests
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        # Create a sample task
        self.task = Task.objects.create(title='Sample Task', description='This is a test task', completed=False)

    def test_list_tasks(self):
        """Test retrieving all tasks"""
        url = reverse('task-list')  # Replace with your router name
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_task(self):
        """Test creating a new task"""
        url = reverse('task-list')
        data = {'title': 'New Task', 'description': 'New task description', 'completed': False}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_retrieve_task(self):
        """Test retrieving a single task"""
        url = reverse('task-detail', args=[self.task.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.task.title)

    def test_update_task(self):
        """Test updating a task"""
        url = reverse('task-detail', args=[self.task.id])
        data = {'title': 'Updated Task', 'description': 'Updated description', 'completed': True}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)
        self.assertEqual(self.task.title, 'Updated Task')

    def test_delete_task(self):
        """Test deleting a task"""
        url = reverse('task-detail', args=[self.task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_unauthenticated_access(self):
        """Test that unauthenticated requests fail"""
        self.client.credentials()  # remove auth
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
