from django.urls import path
from .views import collect_heatmap_data,RunWCAGCheckView, GenerateWCAGReportView

urlpatterns = [
    path('heatmap/', collect_heatmap_data, name='collect_heatmap_data'),
    path('wcag-check/<str:user_id>/<path:website_url>/', RunWCAGCheckView.as_view(), name='run_wcag_check'),
    path('wcag-report/<str:user_id>/<path:website_url>/', GenerateWCAGReportView.as_view(), name='generate_wcag_report'),
]