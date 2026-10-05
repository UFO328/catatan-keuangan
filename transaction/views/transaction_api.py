from rest_framework import viewsets
from drf_spectacular.utils import (
  extend_schema,
  extend_schema_view,
  OpenApiExample,
  OpenApiParameter,
  OpenApiTypes,
)
from ..models import Transaction
from ..serializer import TransactionSerializer
from ..filter_transaction import TransactionFilter


@extend_schema_view(
  list=extend_schema(
    summary="Daftar transaksi",
    description=(
      "Menampilkan seluruh transaksi milik user yang sedang login "
      "(diurutkan berdasarkan tanggal transaksi terbaru), "
      "dengan paginasi 10 data per halaman."
    ),
    parameters=[
      OpenApiParameter(
        "type",
        OpenApiTypes.STR,
        description="Filter berdasarkan jenis transaksi.",
        enum=["INCOME", "EXPENSE"],
      ),
      OpenApiParameter(
        "category",
        OpenApiTypes.INT,
        description="Filter berdasarkan id kategori milik user.",
      ),
      OpenApiParameter(
        "date_from",
        OpenApiTypes.DATE,
        description="Transaksi sejak tanggal ini ( inklusif ).",
      ),
      OpenApiParameter(
        "date_to",
        OpenApiTypes.DATE,
        description="Transaksi sampai tanggal ini ( inklusif ).",
      ),
    ],
  ),
  retrieve=extend_schema(
    summary="Detail transaksi",
    description="Menampilkan satu transaksi berdasarkan id.",
  ),
  create=extend_schema(
    summary="Buat transaksi",
    description=(
      "Mencatat transaksi baru untuk user yang sedang login. "
      "Kategori harus milik user tersebut dan nominal harus lebih dari 0."
    ),
    examples=[
      OpenApiExample(
        "Transaksi pemasukan",
        value={
          "category": 1,
          "type": "INCOME",
          "amount": "50000.00",
          "description": "Gaji bulanan",
          "transaction_date": "2026-10-05T12:00:00Z",
        },
        request_only=True,
      ),
      OpenApiExample(
        "Transaksi pengeluaran",
        value={
          "category": 2,
          "type": "EXPENSE",
          "amount": "15000.00",
          "description": "Makan siang",
          "transaction_date": "2026-10-05T13:30:00Z",
        },
        request_only=True,
      ),
    ],
  ),
  update=extend_schema(
    summary="Perbarui seluruh data transaksi",
  ),
  partial_update=extend_schema(
    summary="Perbarui sebagian data transaksi",
  ),
  destroy=extend_schema(
    summary="Hapus transaksi",
  ),
)
class TransactionAPI(viewsets.ModelViewSet):
  """ViewSet CRUD transaksi (pemasukan / pengeluaran).

  Setiap user hanya bisa melihat dan mengubah transaksinya sendiri.
  """
  serializer_class = TransactionSerializer
  filterset_class = [TransactionFilter]

  def get_queryset(self):
    if getattr(self, "swagger_fake_view", False):
      return Transaction.objects.none()
    queryset = Transaction.objects.filter(user=self.request.user).select_related("category")
    return queryset

  def perform_create(self,serializer):
    serializer.save(user=self.request.user)
