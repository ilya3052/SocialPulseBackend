from django.urls import path

from reports.views import AdminReportPDFView

urlpatterns = [
    path('admin/', AdminReportPDFView.as_view(), name='test_report')
]