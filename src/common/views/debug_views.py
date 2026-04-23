import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.logger import setup_logger
from common.utils.debug_utils import try_parse_json

logger = setup_logger(log_file="../logs/debug.log")


class DebugView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data

        # пробуем распарсить вложенные JSON-строки
        parsed_data = {
            key: try_parse_json(value)
            for key, value in data.items()
        }

        formatted_json = json.dumps(
            parsed_data,
            indent=4,
            ensure_ascii=False
        )

        logger.debug("Incoming request data:\n%s", formatted_json)

        return Response({"status": "ok"}, status=status.HTTP_200_OK)
