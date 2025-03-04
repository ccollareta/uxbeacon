from django.contrib import admin
from .models import WCAGReport

class WCAGReportAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'website_url', 'readability_score', 'missing_alt_text', 'created_at', 'pdf_report_path')
    search_fields = ('user_id', 'website_url')
    list_filter = ('created_at',)

    actions = ['generate_reports']

    def generate_reports(self, request, queryset):
        """Bulk action to generate reports for selected WCAG entries."""
        for report in queryset:
            report.generate_wcag_report()
        self.message_user(request, "Selected WCAG reports have been generated.")
    generate_reports.short_description = "Generate WCAG Reports"

admin.site.register(WCAGReport, WCAGReportAdmin)