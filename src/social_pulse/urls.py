"""
URL configuration for social_pulse project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path, include

from common.views import DebugView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v4/debug/', DebugView.as_view(), name='error'),
    path('api/v4/users/', include('users.urls'), name='users'),
    path('api/v4/auth/', include('social_auth.urls'), name='auth'),
    path('api/v4/admin/', include('social_admin.urls'), name='admin-panel'),
    path('api/v4/service-accounts/', include('service_accounts.urls'), name='service-accounts'),
    path('api/v4/social-entities/', include('social_entities.urls'), name='social-entities'),

]
