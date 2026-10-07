from rest_framework import serializers
from ..models import Category

class CategorySerializer(serializers.ModelSerializer):
  """Serializer kategori transaksi.

  Field `user`, `created_at`, dan `updated_at` diisi otomatis
  (read-only). Nama kategori unik per user.
  """
  class Meta:
    model = Category
    fields = "__all__"
    read_only_fields=['user','created_at','updated_at']

  def validate_name(self,data):
    user = self.context["request"].user
    if Category.objects.filter(name=data,user=user).exists():
      raise serializers.ValidationError("Terjadi Duplikat Category")
    return data
    
  