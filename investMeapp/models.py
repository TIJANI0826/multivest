from django.db import models
from django.utils import timezone
from PIL import Image
from django.contrib.auth.models import User

class Members(models.Model):
    MALE = 'Male'
    FEMALE = 'Female'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]

    ACTIVE = 1
    INACTIVE = 2
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]

    code = models.CharField(max_length=250)
    first_name = models.CharField(max_length=250)
    middle_name = models.CharField(max_length=250, blank=True, null=True)
    last_name = models.CharField(max_length=250)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default=MALE)
    contact = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    address = models.TextField(blank=True, null=True)
    image_path = models.ImageField(upload_to="members/", blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=ACTIVE)
    delete_flag = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_created = models.DateTimeField(auto_now=True)
    bank_account = models.CharField(max_length=250, blank=True, null=True)
    bank_name = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        verbose_name_plural = "List of Members"

    def __str__(self):
        return f"{self.code} - {self.first_name}{' ' + self.middle_name if self.middle_name else ''} {self.last_name}"

    def name(self):
        return f"{self.first_name}{' ' + self.middle_name if self.middle_name else ''} {self.last_name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image_path:
            img = Image.open(self.image_path.path)
            if img.height > 300 or img.width > 300:
                new_img = (300, 300)
                img.thumbnail(new_img)
                img.save(self.image_path.path)

class Investment(models.Model):
    member = models.ForeignKey(Members, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    date_invested = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.member.name()} - {self.amount} on {self.date_invested}"

class MonthlyROI(models.Model):
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE)
    month = models.DateField()
    roi = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.investment.member.name()} - {self.month.strftime('%B %Y')} - ROI: {self.roi}"

class WithdrawalRequest(models.Model):
    member = models.ForeignKey(Members, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_requested = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.member.name()} - {self.amount} - {'Approved' if self.approved else 'Pending'}"
