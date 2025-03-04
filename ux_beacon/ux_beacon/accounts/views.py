# accounts/views.py
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
import json
from django.conf import settings
from .models import SubscriptionPlan, CustomUser

stripe.api_key = settings.STRIPE_SECRET_KEY

class SignupView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        subs = SubscriptionPlan.objects.all()
        return render(request, 'registration/signup.html', {'subscription_plan': subs})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
        return render(request, 'registration/signup.html', {'form': form})

@csrf_exempt
def create_checkout_session(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        subscription_plan_id = data.get("subscription_plan")
        plan = SubscriptionPlan.objects.get(id=subscription_plan_id)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer_email=email,
            line_items=[{
                "price": plan.stripe_price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url="http://127.0.0.1:8000/accounts/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://127.0.0.1:8000/accounts/cancel"
        )

        return JsonResponse({"session_id": checkout_session.id})
    return JsonResponse({"error": "Invalid request"}, status=400)

def stripe_success(request):
    session_id = request.GET.get("session_id")
    if not session_id:
        return JsonResponse({"error": "Invalid session"}, status=400)

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        user = CustomUser.objects.get(stripe_session_id=session_id)
        
        if session.payment_status == "paid":
            user.stripe_subscription_id = session.subscription
            user.subscription_active = True
            user.save()
        
        return redirect('dashboard')
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def stripe_cancel(request):
    return redirect('/accounts/signup')  # Redirect user back to the dashboard


@csrf_exempt
def create_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            if data["password1"] != data["password2"]:
                return JsonResponse({"error": "Passwords do not match"}, status=400)

            user = CustomUser.objects.create(
                username=data["username"],
                email=data["email"],
                company_name=data.get("company_name", ""),
                website=data.get("website", ""),
                phone_number=data.get("phone_number", "")
            )
            user.set_password(data["password1"])
            user.save()

            # Create Stripe customer
            customer = stripe.Customer.create(email=user.email)
            user.stripe_customer_id = customer.id
            user.save()

            # Create payment intent
            plan = SubscriptionPlan.objects.get(stripe_price_id=data["subscription_plan"])
            payment_intent = stripe.PaymentIntent.create(
                amount=int(plan.price_per_month * 100),  
                currency="usd",
                customer=customer.id,
                automatic_payment_methods={"enabled": True},
            )

            return JsonResponse({"clientSecret": payment_intent.client_secret})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
