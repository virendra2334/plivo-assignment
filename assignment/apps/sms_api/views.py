#from django.shortcuts import render

# Create your views here.

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from .authentication import AccountBasicAuthentication

class BaseView(APIView):
    authentication_classes = [AccountBasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        return Response('hello ji')
