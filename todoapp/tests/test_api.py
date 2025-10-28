from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from todoapp.models import Task


class TodoAPITest(APITestCase):
    """Comprehensive API tests for the Todo app"""

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Obtain JWT token for authentication
        url = reverse('token_obtain_pair')  # Must match your urls.py
        response = self.client.post(url, {'username': 'testuser', 'password': 'testpass'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data['access']

        # Set authorization header for all future requests
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        # Create a sample task
        self.task = Task.objects.create(title='Sample Task', description='This is a test task', completed=False)

    # ---------------------------------------------------------------------
    # CORE CRUD TESTS
    # ---------------------------------------------------------------------

    def test_list_tasks(self):
        """Test retrieving all tasks"""
        url = reverse('task-list')
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

    # ---------------------------------------------------------------------
    # AUTHENTICATION & PERMISSIONS
    # ---------------------------------------------------------------------

    def test_unauthenticated_access(self):
        """Test that unauthenticated requests are denied"""
        self.client.credentials()  # remove auth
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_token_access(self):
        """Test that requests with an invalid token are rejected"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken123')
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_access_other_users_task(self):
        """Ensure a user cannot access another user's tasks"""
        other_user = User.objects.create_user(username='other', password='pass123')
        other_task = Task.objects.create(title='Other Task', description='Not yours', completed=False)

        url = reverse('task-detail', args=[other_task.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    # ---------------------------------------------------------------------
    # EDGE CASES & VALIDATION
    # ---------------------------------------------------------------------

    def test_partial_update_task(self):
        """Test partially updating a task (PATCH)"""
        url = reverse('task-detail', args=[self.task.id])
        data = {'completed': True}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)

    def test_create_task_with_invalid_data(self):
        """Test creating a task with missing required fields"""
        url = reverse('task-list')
        data = {'description': 'Missing title field'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_nonexistent_task(self):
        """Test retrieving a task that doesn't exist"""
        url = reverse('task-detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_empty_tasks(self):
        """Test listing tasks when no tasks exist"""
        Task.objects.all().delete()
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # ---------------------------------------------------------------------
    # MODEL BEHAVIOR
    # ---------------------------------------------------------------------

    def test_task_str_representation(self):
        """Test Task model string representation"""
        self.assertEqual(str(self.task), self.task.title)

    # ---------------------------------------------------------------------
    # OPTIONAL: Filtering or Search (if supported)
    # ---------------------------------------------------------------------

    def test_filter_completed_tasks(self):
        """Test filtering tasks by completion status (if implemented)"""
        Task.objects.create(title='Done', completed=True)
        url = reverse('task-list') + '?completed=true'
        response = self.client.get(url)
        # Not all APIs implement this, so ignore if unsupported
        if response.status_code == status.HTTP_200_OK:
            for task in response.data:
                self.assertTrue(task.get('completed', False))
