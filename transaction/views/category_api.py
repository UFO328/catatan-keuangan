from rest_framework import viewsets,status
from rest_framework.response import Response
from drf_spectacular.utils import (
  extend_schema,
  extend_schema_view,
  OpenApiExample,
)
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from ..models import Category
from ..serializer import CategorySerializer


@extend_schema_view(
  list=extend_schema(
    summary="Daftar kategori",
    description=(
      "Menampilkan seluruh kategori milik user yang sedang login, "
      "diurutkan berdasarkan nama."
    ),
  ),
  retrieve=extend_schema(
    summary="Detail kategori",
  ),
  create=extend_schema(
    summary="Buat kategori",
    description=(
      "Membuat kategori baru untuk user yang sedang login. "
      "Nama kategori harus unik per user."
    ),
    examples=[
      OpenApiExample(
        "Contoh request",
        value={"name": "Hadiah", "is_default": False},
        request_only=True,
      ),
    ],
  ),
  update=extend_schema(
    summary="Perbarui seluruh data kategori",
  ),
  partial_update=extend_schema(
    summary="Perbarui sebagian data kategori",
  ),
  destroy=extend_schema(
    summary="Hapus kategori",
    description="Kategori yang sudah dipakai transaksi tidak bisa dihapus.",
  ),
)
class CategoryAPI(viewsets.ModelViewSet):
  """ViewSet CRUD kategori transaksi.

  Kategori bersifat unik per user; kategori default
  dibuat otomatis saat user mendaftar.
  """
  serializer_class = CategorySerializer

  def get_queryset(self):
    queryset = Category.objects.filter(user=self.request.user).select_related("user")
    return queryset

  def perform_create(self,serializer):
    serializer.save(user=self.request.user)

  def destroy(self,request,*args,**kwargs):
    try:
      return super().destroy(request,*args,**kwargs)
    except ProtectedError:
      return Response({"detail":"Category Tidak Bisa Di Hapus"},status=status.HTTP_400_BAD_REQUEST)
    

  
