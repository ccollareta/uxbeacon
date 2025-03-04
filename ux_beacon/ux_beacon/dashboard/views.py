from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import stripe
import json
import requests
from .forms import WebsiteForm
from .models import Websites, HeatmapData, AuditResult

@login_required
def dashboard(request):
    websites = Websites.objects.filter(user=request.user)
    return render(request, 'dashboard/dashboard.html', {'websites': websites})

@login_required
def add_website(request):
    form = WebsiteForm()
    if request.method == 'POST':
        url = request.POST['url']
        website = Websites.objects.create(user=request.user, url=url)
        return redirect('dashboard')
    return render(request, 'dashboard/add_website.html',{'form': form})

@login_required
def view_heatmap(request, website_id):
    website = get_object_or_404(Websites, id=website_id, user=request.user)
    heatmap_data = HeatmapData.objects.filter(website=website)
    return render(request, 'dashboard/heatmap.html', {'website': website, 'heatmap_data': heatmap_data})

@login_required
def run_audit(request, website_id):
    website = get_object_or_404(Websites, id=website_id, user=request.user)
    ux_score = 85  # Placeholder for AI analysis
    ada_compliance = True  # Placeholder for ADA check
    AuditResult.objects.create(website=website, ux_score=ux_score, ada_compliance=ada_compliance)
    return redirect('dashboard')


@csrf_exempt
def collect_heatmap_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        website = Websites.objects.filter(user__user_id=user_id).first()
        if website:
            HeatmapData.objects.create(website=website, data=data)
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)