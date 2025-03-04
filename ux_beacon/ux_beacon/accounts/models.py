import random
import string
from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from django.utils.timezone import now
from django.contrib import admin
from django_otp.plugins.otp_totp.models import TOTPDevice
import stripe
from django.conf import settings
from django import forms


stripe.api_key = settings.STRIPE_SECRET_KEY

def generate_user_id():
    """Generate a unique user ID starting with 'UXB-' followed by alphanumeric characters."""
    return "UXB-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=255)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(max_length=255, unique=True)
    permission = models.ForeignKey(Permission, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    user_id = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    subscription_active = models.BooleanField(default=False)
    subscription_end_date = models.DateField(blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)  # New field
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = generate_user_id()
        super().save(*args, **kwargs)

    def check_subscription_status(self):
        if self.subscription_end_date and self.subscription_end_date < now().date():
            self.subscription_active = False
            self.save()
    
    def enable_totp(self):
        if not TOTPDevice.objects.filter(user=self).exists():
            device = TOTPDevice.objects.create(user=self, confirmed=False)
            return device.config_url  # Provide QR Code URL for setup
        return None
    
    def disable_totp(self):
        TOTPDevice.objects.filter(user=self).delete()
    
    def has_totp_enabled(self):
        return TOTPDevice.objects.filter(user=self, confirmed=True).exists()
    
    def create_stripe_customer(self, email):
        if not self.stripe_customer_id:
            customer = stripe.Customer.create(email=email)
            self.stripe_customer_id = customer.id
            self.save()
    
    def subscribe(self, stripe_price_id, subscription_plan):
        if not self.stripe_customer_id:
            self.create_stripe_customer(self.email)
        
        subscription = stripe.Subscription.create(
            customer=self.stripe_customer_id,
            items=[{'price': stripe_price_id}],
            expand=['latest_invoice.payment_intent']
        )
        self.stripe_subscription_id = subscription.id
        self.subscription_active = True
        self.subscription_end_date = now().date().replace(day=1)  # Simulating 1-month validity
        self.subscription_plan = subscription_plan
        if subscription_plan.permission:
            self.user_permissions.add(subscription_plan.permission)
        self.save()
