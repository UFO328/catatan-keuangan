from rest_framework.views import APIView 
from rest_framework import status 
from rest_framework.response import Response 
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

class LogOutAPI(APIView):
  def post(self):
    try:
      token = RefreshToken(self.request.data.get("refresh"))
      token.blacklist()
    except TokenError:
      return Response({'detail:Token Tidak Valid'},status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_205_RESET_CONTENT)