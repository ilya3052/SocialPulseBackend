from django.urls import path

from service_accounts.views import ServiceAccountsView

urlpatterns = [
    path('summary/', ServiceAccountsView.as_view({"get": "list"}), name='get-service-accounts-info'),
    path('<int:pk>', ServiceAccountsView.as_view({"patch": "partial_update"}),
         name='update-service-account'),
    path('<str:platform>', ServiceAccountsView.as_view({"get": "retrieve"}),
         name='get-service-account'),
    path('', ServiceAccountsView.as_view({"post": "create"}), name='create-service-account'),
]
