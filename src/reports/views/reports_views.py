from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from service_accounts.services import get_service_accounts_aggregated_info, get_service_accounts_loading
from social_entities.services import get_group_aggregated_info
from ..utils.admin_reports import generate_admin_report_excel, generate_admin_report_pdf


class AdminReportPDFView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, *args, **kwargs):
        report_type = request.GET.dict().get('type', 'pdf')
        data = {
            "service_account_loading": get_service_accounts_loading(),
            "service_account_aggregated_info": get_service_accounts_aggregated_info(),
            "group_aggregated_info": get_group_aggregated_info()
        }
        filepath, relative_path = generate_admin_report_excel(data)
        if report_type == 'xlsx':
            return Response(relative_path, status=status.HTTP_200_OK)
        else:
            filepath_pdf = generate_admin_report_pdf(filepath)

        return Response(filepath_pdf, status=status.HTTP_200_OK)