from rest_framework.views import APIView
from transaction.models import Transaction,Category 
from rest_framework.response import Response
from django.db.models import Sum,F
from drf_spectacular.utils import (
  extend_schema,
  OpenApiExample,
  inline_serializer,
)
from rest_framework import serializers


ExpenseByCategory = inline_serializer(
  "ExpenseByCategory",
  fields={
    "category_name": serializers.CharField(),
    "total_expense": serializers.DecimalField(max_digits=15, decimal_places=2),
  },
)
IncomeByCategory = inline_serializer(
  "IncomeByCategory",
  fields={
    "category_name": serializers.CharField(),
    "total_income": serializers.DecimalField(max_digits=15, decimal_places=2),
  },
)
DashboardResponse = inline_serializer(
  "DashboardResponse",
  fields={
    "total_income": serializers.DecimalField(max_digits=15, decimal_places=2),
    "total_expense": serializers.DecimalField(max_digits=15, decimal_places=2),
    "total_expense_by_category": serializers.ListField(child=ExpenseByCategory),
    "total_income_by_category": serializers.ListField(child=IncomeByCategory),
  },
)


@extend_schema(
  summary="Dashboard ringkasan keuangan",
  description=(
    "Menampilkan ringkasan keuangan user yang sedang login: "
    "total pemasukan, total pengeluaran, "
    "serta rincian pemasukan dan pengeluaran per kategori."
  ),
  responses={200: DashboardResponse},
  examples=[
    OpenApiExample(
      "Contoh response sukses",
      value={
        "total_income": "10000000.00",
        "total_expense": "2500000.00",
        "total_expense_by_category": [
          {"category_name": "Makan", "total_expense": "1500000.00"},
          {"category_name": "Transportasi", "total_expense": "1000000.00"},
        ],
        "total_income_by_category": [
          {"category_name": "Gaji", "total_income": "10000000.00"},
        ],
      },
      response_only=True,
    ),
  ],
  tags=["dashboard"],
)
class DashboardMoneyTracker(APIView):
  """Endpoint dashboard: ringkasan pemasukan & pengeluaran user yang login."""

  def get(self,request):
    qs = Transaction.objects.select_related('category').filter(user=self.request.user)
    
    total_income = qs.filter(type="INCOME").aggregate(Sum("amount"))["amount__sum"] or 0 
    total_expense = qs.filter(type="EXPENSE").aggregate(Sum("amount"))["amount__sum"] or 0 

    total_expense_by_category = qs.filter(type="EXPENSE").values(category_name=F("category__name")).annotate(total_expense=Sum("amount"))
    total_income_by_category = qs.filter(type="INCOME").values(category_name=F("category__name")).annotate(total_income=Sum("amount"))
    
    return Response({
      "total_income":total_income,
      "total_expense":total_expense,
      "total_expense_by_category":total_expense_by_category,
      "total_income_by_category":total_income_by_category
    })

    
    

    

    