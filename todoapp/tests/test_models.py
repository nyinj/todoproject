from django.test import TestCase
from todoapp.models import Task

class TaskModelTest(TestCase):
    """Test Task model behavior"""

    def test_str_representation(self):
        task = Task.objects.create(title="My Task")
        self.assertEqual(str(task), "My Task")
