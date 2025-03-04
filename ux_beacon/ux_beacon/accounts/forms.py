# accounts/forms.py
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser,SubscriptionPlan
from django import forms


class CustomUserCreationForm(UserCreationForm):
    subscription_plan = forms.ModelChoiceField(queryset=SubscriptionPlan.objects.all(), required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'company_name', 'website', 'phone_number', 'subscription_plan')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.create_stripe_customer(user.email)
        if commit:
            user.save()
            user.subscribe(self.cleaned_data['subscription_plan'].stripe_price_id, self.cleaned_data['subscription_plan'])
        return user

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email")