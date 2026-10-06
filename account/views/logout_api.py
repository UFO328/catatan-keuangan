from rest_framework.views import APIView
from drf_spectacular.utils import (
  extend_schema,
  OpenApiExample,
  inline_serializer,
  OpenApiResponse,
)
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

LogoutRequest = inline_serializer(
  "LogoutRequest",
  fields={"refresh": serializers.CharField()},
)


@extend_schema(
  summary="Logout (blacklist refresh token)",
  description=(
    "Men-blacklist refresh token sehingga token tersebut tidak bisa "
    "dipakai lagi untuk mendapatkan access token baru."
  ),
  request=LogoutRequest,
  responses={
    205: OpenApiResponse(description="Token berhasil di-blacklist."),
    400: OpenApiResponse(description="Token tidak valid."),
  },
  examples=[
    OpenApiExample(
      "Contoh request",
      value={"refresh": "eyJhbGciOiJIUzI1NiIs..."},
      request_only=True,
    ),
  ],
  tags=["auth"],
)
class LogOutAPI(APIView):
  """Endpoint logout dengan cara men-blacklist refresh token."""
  def post(self,request):
    try:
      token = RefreshToken(self.request.data.get("refresh"))
      token.blacklist()
    except TokenError:
      return Response({'detail':'Token Tidak Valid'},status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_205_RESET_CONTENT)
