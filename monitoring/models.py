from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("user", "User"),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")

    def __str__(self):
        return self.username


class Device(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="devices"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Reading(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    ph = models.FloatField()
    tds = models.FloatField()
    ntu = models.FloatField()
    battery = models.FloatField(null=True, blank=True)
    signal = models.FloatField(null=True, blank=True)
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="readings", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reading {self.pk} - {self.timestamp}"


class Forecast(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    ph_forecast = models.FloatField()
    tds_forecast = models.FloatField()
    ntu_forecast = models.FloatField()
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="forecasts",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Forecast {self.pk} - {self.timestamp}"


class SensorData(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    sensor_type = models.CharField(max_length=50)
    value = models.FloatField()
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="sensor_data"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sensor_type} - {self.value}"


class Alert(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    severity = models.CharField(
        max_length=20, choices=(("LOW", "Low"), ("MEDIUM", "Medium"), ("HIGH", "High"))
    )
    type = models.CharField(
        max_length=20,
        choices=(("RULE", "Rule"), ("AI", "AI"), ("FORECAST", "Forecast")),
    )
    status = models.CharField(
        max_length=20,
        choices=(("NEW", "New"), ("ACK", "Acknowledged"), ("RESOLVED", "Resolved")),
    )
    device = models.ForeignKey(
        Device, on_delete=models.SET_NULL, null=True, blank=True, related_name="alerts"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert {self.pk} - {self.severity}"


class Report(models.Model):
    REPORT_TYPE_CHOICES = (
        ("READING", "Reading"),
        ("FORECAST", "Forecast"),
        ("MIXED", "Mixed"),
    )

    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="reports_created"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reports_received"
    )

    device = models.ForeignKey(
        Device, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports"
    )

    readings = models.ManyToManyField(Reading, blank=True, related_name="reports")
    forecasts = models.ManyToManyField(Forecast, blank=True, related_name="reports")

    content = models.TextField()
    status = models.CharField(
        max_length=20, choices=(("DRAFT", "Draft"), ("SENT", "Sent")), default="DRAFT"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} → {self.recipient.username}"
