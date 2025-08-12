from django.db import models
from django.utils import timezone

class FaxRecord(models.Model):
    """Model for storing fax records"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    fax_id = models.CharField(max_length=100, unique=True)
    to_number = models.CharField(max_length=20)
    from_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    media_url = models.URLField(blank=True, null=True)
    subject = models.CharField(max_length=200, blank=True, null=True)
    num_pages = models.IntegerField(default=1)
    direction = models.CharField(max_length=10, default='outbound')
    patient_name = models.CharField(max_length=200, blank=True, null=True)
    device_type = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Fax {self.fax_id} to {self.to_number}"

class SMSRecord(models.Model):
    """Model for storing SMS records"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]
    
    sid = models.CharField(max_length=100, unique=True)
    to_number = models.CharField(max_length=20)
    from_number = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"SMS {self.sid} to {self.to_number}"

class APIConfiguration(models.Model):
    """Model for storing API configuration"""
    SERVICE_CHOICES = [
        ('telnyx', 'Telnyx'),
        ('humblefax', 'HumbleFax'),
        ('twilio', 'Twilio'),
    ]
    
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    secret_key = models.CharField(max_length=255, blank=True, null=True)
    account_sid = models.CharField(max_length=255, blank=True, null=True)
    auth_token = models.CharField(max_length=255, blank=True, null=True)
    from_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['service']
    
    def __str__(self):
        return f"{self.service} Configuration"
