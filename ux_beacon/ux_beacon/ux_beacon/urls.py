"""
URL configuration for ux_beacon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView
from ux_beacon.views import HomePageView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings



urlpatterns = [
    path("", HomePageView.as_view(), name="home"), 
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("dashboard/", include("dashboard.urls")),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls'))
    
] + staticfiles_urlpatterns()
