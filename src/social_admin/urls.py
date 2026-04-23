from django.urls import path

from social_admin.views import SummaryAdminPanelView

urlpatterns = [
    path('summary/', SummaryAdminPanelView.as_view(), name='summary-admin-panel'),
]
