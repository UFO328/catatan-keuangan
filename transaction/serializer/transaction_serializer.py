from rest_framework import serializers 
from ..models import Transaction 

class TransactionSerializer(serializers.ModelSerializer):
  class Meta:
    model = Transaction
    fields = "__all__"
    read_only_fields=['user','created_at','updated_at']

  def validate_category(self, value):
    request = self.context["request"]
    if value.user != request.user:
      raise serializers.ValidationError("Category tidak ditemukan.")
    return value

  def validate_amount(self,amount):
    if amount <= 0:
      raise serializers.ValidationError({"amount":"Nilai Harus Lebih Dari 0"})
    return amount