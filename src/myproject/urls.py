"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path

from myapp.views import (
    AddReadingsView,
    ListReadingsByDeviceView,
    ListReadingsByCustomerView,
)

urlpatterns = [
    path('api/readings/', AddReadingsView.as_view(), name='api-readings'),
    path('api/device/<uuid:device_id>/readings/avg/', ListReadingsByDeviceView.as_view(), name='api-device-readings'),
    path('api/customer/<uuid:customer_id>/readings/avg/', ListReadingsByCustomerView.as_view(), name='api-customer-readings'),
    path('admin/', admin.site.urls),
]
