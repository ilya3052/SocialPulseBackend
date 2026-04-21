from django.urls import path

from admin_panel.views import PlatformsView, ServiceAccountsView

urlpatterns = [
    path('platforms/', PlatformsView.as_view({"get": "list", "post": "create"}), name='platforms'),
    path('service-account/', ServiceAccountsView.as_view(), name='add-service-account'),
]