from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from monitoring.models import Device, Reading

User = get_user_model()


class BasicViewTests(TestCase):
    """Basic tests for main views"""

    def test_home_view_accessible(self):
        """Test that home view is accessible"""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_login_view_accessible(self):
        """Test that login view is accessible"""
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)


class UserModelTests(TestCase):
    """Tests for User model"""

    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))


class DeviceModelTests(TestCase):
    """Tests for Device model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_create_device(self):
        """Test creating a device"""
        device = Device.objects.create(
            name="Test Device", location="Test Location", user=self.user
        )
        self.assertEqual(device.name, "Test Device")
        self.assertEqual(device.location, "Test Location")
        self.assertEqual(device.user, self.user)


class ReadingModelTests(TestCase):
    """Tests for Reading model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.device = Device.objects.create(
            name="Test Device", location="Test Location", user=self.user
        )

    def test_create_reading(self):
        """Test creating a water quality reading"""
        reading = Reading.objects.create(device=self.device, ph=7.0, tds=150.0, ntu=2.5)
        self.assertEqual(reading.device, self.device)
        self.assertEqual(reading.ph, 7.0)
        self.assertEqual(reading.tds, 150.0)
        self.assertEqual(reading.ntu, 2.5)

    def test_reading_str_method(self):
        """Test the string representation of Reading"""
        reading = Reading.objects.create(device=self.device, ph=7.0, tds=150.0, ntu=2.5)
        expected = f"{self.device.name} - {reading.timestamp}"
        self.assertEqual(str(reading), expected)


class APIViewTests(TestCase):
    """Tests for API endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.device = Device.objects.create(name="Test Device", user=self.user)

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
