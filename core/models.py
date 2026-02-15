import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Extend User model (optional, but good for roles)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    location = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default-avatar.png')
    phone = models.CharField(max_length=15, null=True)
    coins = models.IntegerField(default=0) # Starting coins
    certificate_unlocked = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Evidence(models.Model):
    MEMO_TYPE_CHOICES = (
        ('Image', 'Image'),
        ('Video', 'Video'),
    )
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    memo_id = models.CharField(max_length=50, null=True, blank=True)
    file = models.FileField(upload_to='evidence/')
    location = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # AI Verification Status
    is_verified = models.BooleanField(default=False)
    is_fake = models.BooleanField(default=False) # Fake/Original check
    detected_plate = models.CharField(max_length=20, blank=True, null=True)
    violation_type = models.CharField(max_length=10, choices=MEMO_TYPE_CHOICES) # e.g., "No Helmet"

    def save(self, *args, **kwargs):
        if not self.memo_id:
            self.memo_id = f"MEMO-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
       return f"Evidence - {self.memo_id}" if self.memo_id else f"Evidence ID {self.id}"


class Challan(models.Model):
    STATUS_CHOICES = [
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
    ]
    vehicle_number = models.CharField(max_length=20)
    violator_name = models.CharField(max_length=100, default="Unknown")
    violation_type = models.CharField(max_length=100)
    amount = models.PositiveIntegerField()
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unpaid') # Paid/Unpaid
    evidence = models.ForeignKey(Evidence , null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.vehicle_number}  - ₹{self.amount} - {self.violation_type} -{self.status}"
    
class FIR(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    image = models.ImageField(upload_to='firs/')
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='Pending')
    date_filed = models.DateTimeField(auto_now_add=True)

class MemoEvidence(models.Model):
    MEMO_TYPE_CHOICES = (
        ('Image', 'Image'),
        ('Video', 'Video'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    )

    memo_id = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=255)
    evidence_type = models.CharField(max_length=10, choices=MEMO_TYPE_CHOICES)
    evidence_file = models.FileField(upload_to='evidence/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.memo_id
    
class DetectionBoundary(models.Model):
    name = models.CharField(max_length=150)
    start_point = models.CharField(max_length=255)
    end_point = models.CharField(max_length=255)
    length_km = models.DecimalField(max_digits=6, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)