from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_panel.utils import get_group_aggregated_info, get_service_accounts_aggregated_info, \
    get_service_accounts_loading


class SummaryAdminPanelView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        group_data = get_group_aggregated_info()
        service_account_data = get_service_accounts_aggregated_info()
        service_account_loading = get_service_accounts_loading()

        return Response({
            "group_info": {
                **group_data,
            },
            "service_account_info": {
                **service_account_data,
            },
            "service_account_loading_info": {
                **service_account_loading
            }
        }, status=status.HTTP_200_OK)
