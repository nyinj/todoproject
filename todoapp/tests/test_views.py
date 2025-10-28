from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class TodoViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_login_page_renders(self):
        url = reverse('login')  # match your urls.py
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign in")
