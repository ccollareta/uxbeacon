# accounts/urls.py
from django.urls import path

from .views import SignupView, create_checkout_session,stripe_success, stripe_cancel,create_user


urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("create-checkout-session/", create_checkout_session, name="create_checkout_session"),
    path('create-user/', create_user, name='create_user'),
    path('success/', stripe_success, name="stripe_success"),
    path('cancel/', stripe_cancel, name="stripe_cancel" ),
]