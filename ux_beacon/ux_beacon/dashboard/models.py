from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.conf import settings
import stripe
import requests

stripe.api_key = settings.STRIPE_SECRET_KEY

class Websites(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    url = models.URLField(unique=True)
    tracking_code = models.CharField(max_length=255, unique=True, blank=True)
    screenshot = models.ImageField(upload_to='screenshots/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = f"<script src='/track.js?uid={self.user.user_id}'></script>"
        super().save(*args, **kwargs)

class HeatmapData(models.Model):
    website = models.ForeignKey(Websites, on_delete=models.CASCADE)
    data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

class AuditResult(models.Model):
    website = models.ForeignKey(Websites, on_delete=models.CASCADE)
    ux_score = models.IntegerField()
    ada_compliance = models.BooleanField()
    generated_at = models.DateTimeField(auto_now_add=True)
