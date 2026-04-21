from django.urls import path

from admin_panel.views import PlatformsView, ServiceAccountsView, SummaryAdminPanelView, LoadingOnServiceAccounts

urlpatterns = [
    path('platforms/', PlatformsView.as_view({"get": "list", "post": "create"}), name='platforms'),
    path('service-accounts/', ServiceAccountsView.as_view({"get": "list", "post": "create"}), name='add-service-account'),
    path('service-accounts/<str:platform>/', ServiceAccountsView.as_view({"get": "retrieve"}), name='add-service-account'),
    path('service-accounts/loading', LoadingOnServiceAccounts.as_view(), name='service-account-loading'),
    # главная страница панели
    path('summary/', SummaryAdminPanelView.as_view(), name='summary-admin-panel'),
]