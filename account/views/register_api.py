from rest_framework.views import APIView
from drf_spectacular.utils import (
  extend_schema,
  OpenApiExample,
  inline_serializer,
  OpenApiResponse,
)
from rest_framework import serializers
from ..serializer import RegisterSerializer
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response

RegisterResponse = inline_serializer(
  "RegisterResponse",
  fields={"message": serializers.CharField()},
)


class RegisterAPI(APIView):
  """Endpoint registrasi akun baru.

  Setelah akun berhasil dibuat, kategori default
  (Makan, Transportasi, Belanja, Tagihan, Hiburan, Uang Saku, Lainnya)
  otomatis dibuatkan untuk user tersebut.
  """
  permission_classes = [AllowAny]

  @extend_schema(
    summary="Registrasi akun baru",
    description=(
      "Mendaftarkan user baru. Username dan email harus unik. "
      "Password divalidasi menggunakan password validator bawaan Django."
    ),
    request=RegisterSerializer,
    responses={
      201: RegisterResponse,
      400: OpenApiResponse(
        description=(
          "Data tidak valid: username/email sudah dipakai, "
          "email tidak valid, atau password tidak memenuhi kriteria."
        )
      ),
    },
    examples=[
      OpenApiExample(
        "Contoh request",
        value={
          "username": "riski",
          "email": "riski@example.com",
          "password": "passwordku123",
        },
        request_only=True,
      ),
      OpenApiExample(
        "Contoh response sukses",
        value={"message": "Account Berhasil Dibuat"},
        response_only=True,
      ),
    ],
    tags=["auth"],
  )
  def post(self,request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"message":"Account Berhasil Dibuat"},status=status.HTTP_201_CREATED)
