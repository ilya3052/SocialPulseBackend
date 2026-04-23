from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView


class SummaryAdminPanelView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        from service_accounts.services import get_service_accounts_aggregated_info, get_service_accounts_loading
        from social_entities.services import get_group_aggregated_info
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
