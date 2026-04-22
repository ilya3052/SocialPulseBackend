from django.urls import path

from admin_panel.views import PlatformsView, ServiceAccountsView, SummaryAdminPanelView

urlpatterns = [
    path('platforms/', PlatformsView.as_view({"get": "list", "post": "create"}), name='platforms'),
    # главная страница панели
    path('summary/', SummaryAdminPanelView.as_view(), name='summary-admin-panel'),
    path('service-accounts/summary/', ServiceAccountsView.as_view({"get": "list"}), name='get-service-accounts-info'),
    path('service-accounts/<int:pk>/', ServiceAccountsView.as_view({"patch": "partial_update"}),
         name='update-service-account'),
    path('service-accounts/<str:platform>/', ServiceAccountsView.as_view({"get": "retrieve"}),
         name='get-service-account'),
    path('service-accounts/', ServiceAccountsView.as_view({"post": "create"}), name='create-service-account'),

]
