from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from monitoring.models import Device, Reading

User = get_user_model()


class BasicViewTests(TestCase):
    """Basic tests for main views"""
    
    def test_home_view_accessible(self):
        """Test that home view is accessible"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_view_accessible(self):
        """Test that login view is accessible"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_register_view_accessible(self):
        """Test that register view is accessible"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)


class ModelTests(TestCase):
    """Basic model tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """Test user model creation"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_device_creation(self):
        """Test device model creation"""
        device = Device.objects.create(
            name='Test Device',
            location='Test Lab',
            description='Test ESP32 device',
            user=self.user
        )
        self.assertEqual(device.name, 'Test Device')
        self.assertEqual(device.location, 'Test Lab')
        self.assertEqual(device.user, self.user)
    
    def test_reading_creation(self):
        """Test reading model creation"""
        device = Device.objects.create(
            name='Test Device',
            location='Test Lab',
            user=self.user
        )
        reading = Reading.objects.create(
            device=device,
            ph=7.5,
            tds=150.0,
            ntu=2.5
        )
        self.assertEqual(reading.device, device)
        self.assertEqual(reading.ph, 7.5)
        self.assertEqual(reading.tds, 150.0)
        self.assertEqual(reading.ntu, 2.5)


class AuthenticationTests(TestCase):
    """Authentication related tests"""
    
    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_login(self):
        """Test user can login"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
    
    def test_dashboard_requires_auth(self):
        """Test dashboard requires authentication"""
        response = self.client.get(reverse('dashboard'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response['Location'])
    
    def test_dashboard_accessible_when_logged_in(self):
        """Test dashboard accessible when user is logged in"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)