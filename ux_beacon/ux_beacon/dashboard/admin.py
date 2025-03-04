from django.contrib import admin
from .models import Websites, AuditResult, HeatmapData
# Register your models here.


admin.site.register(Websites)
admin.site.register(AuditResult)
admin.site.register(HeatmapData)