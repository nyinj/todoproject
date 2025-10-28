from todoapp.models import Task
from django.contrib.auth.models import User

def create_test_user(username='testuser', password='testpass'):
    user = User.objects.create_user(username=username, password=password)
    return user

def create_task(user, title='Sample Task', description='Test', completed=False):
    return Task.objects.create(title=title, description=description, completed=completed)
