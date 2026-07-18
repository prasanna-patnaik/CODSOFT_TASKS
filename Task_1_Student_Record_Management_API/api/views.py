from rest_framework.views import APIView
from rest_framework.response import Response

class HomeAPIView(APIView):

    def get(self, request):

        data = {
            "message": "Welcome to Student Record Management API"
        }

        return Response(data)