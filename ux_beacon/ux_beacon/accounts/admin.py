# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, SubscriptionPlan


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'user_id', 'email', 'company_name', 'subscription_active', 'subscription_end_date', 'subscription_plan')
    search_fields = ('username', 'email', 'company_name')
    list_filter = ('subscription_active', 'subscription_end_date', 'subscription_plan')
    actions = ['mark_subscription_active', 'mark_subscription_inactive']
    
    def mark_subscription_active(self, request, queryset):
        queryset.update(subscription_active=True)
    mark_subscription_active.short_description = "Mark selected users as active subscribers"
    
    def mark_subscription_inactive(self, request, queryset):
        queryset.update(subscription_active=False)
    mark_subscription_inactive.short_description = "Mark selected users as inactive subscribers"

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SubscriptionPlan)