from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password123',
            first_name='Test'
        )

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_post_valid(self):
        response = self.client.post(reverse('login'), {
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('home'))

    def test_login_post_invalid(self):
        response = self.client.post(reverse('login'), {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'planner/register.html')

    def test_register_post_valid(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'NewUser',
            'email': 'new@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        })
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_authenticated_navbar(self):
        self.client.login(username='test@example.com', password='password123')
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Hey, Test!')
        self.assertNotContains(response, 'Log in')
