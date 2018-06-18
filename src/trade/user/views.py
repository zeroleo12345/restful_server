from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

from trade.user.serializer import UserSerializer


class UnusedView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        return Response()

    def post(self, request):
        return Response()


class UserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
