content://com.termux.documents/tree/%2Fdata%2Fdata%2Fcom.termux%2Ffiles%2Fhome::/data/data/com.termux/files/home/catatan_keuangan/account/views/login_api.pyfrom rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import (
  extend_schema,
  OpenApiExample,
  inline_serializer,
  OpenApiResponse,
)
from rest_framework import serializers
from ..serializer import LoginSerializer

TokenPairResponse = inline_serializer(
  "TokenPairResponse",
  fields={
    "access": serializers.CharField(),
    "refresh": serializers.CharField(),
    "username": serializers.CharField(),
    "id": serializers.IntegerField(),
  },
)


@extend_schema(
  summary="Login akun",
  description=(
    "Mengembalikan pasangan access token & refresh token JWT "
    "(access aktif 15 menit, refresh aktif 7 hari), "
    "beserta username dan id user."
  ),
  request=LoginSerializer,
  responses={
    200: TokenPairResponse,
    401: OpenApiResponse(description="Kredensial tidak valid."),
  },
  examples=[
    OpenApiExample(
      "Contoh request",
      value={"username": "riski", "password": "passwordku123"},
      request_only=True,
    ),
    OpenApiExample(
      "Contoh response sukses",
      value={
        "access": "eyJhbGciOiJIUzI1NiIs...",
        "refresh": "eyJhbGciOiJIUzI1NiIs...",
        "username": "riski",
        "id": 1,
      },
      response_only=True,
    ),
  ],
  tags=["auth"],
)
class LoginAPI(TokenObtainPairView):
  """Endpoint login yang mengembalikan JWT access & refresh token."""
  serializer_class = LoginSerializer
