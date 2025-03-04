from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from dashboard.models import HeatmapData, Websites
from django.views import View
from .models import WCAGReport
import os

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



class RunWCAGCheckView(View):
    """View to run WCAG check using Django models."""

    def get(self, request, user_id, website_url):
        try:
            wcag_report, created = WCAGReport.objects.get_or_create(user_id=user_id, website_url=website_url)
            wcag_report.run_wcag_check()
            return JsonResponse({"status": "success", "message": "WCAG check completed"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

class GenerateWCAGReportView(View):
    """View to generate a WCAG report and return it as a downloadable PDF."""

    def get(self, request, user_id, website_url):
        try:
            wcag_report = WCAGReport.objects.filter(user_id=user_id, website_url=website_url).latest('created_at')
            pdf_path = wcag_report.generate_wcag_report()

            if not pdf_path or not os.path.exists(pdf_path):
                return JsonResponse({"status": "error", "message": "Report generation failed"}, status=500)

            with open(pdf_path, 'rb') as pdf:
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="WCAG_Report_{user_id}.pdf"'
                return response
        except WCAGReport.DoesNotExist:
            return JsonResponse({"status": "error", "message": "No report found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
