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
    queryset = Category.objects.filter(name=data,user=user)
    if self.instance is not None:
      queryset = queryset.exclude(pk=self.instance.pk)
    if queryset.exists():
      raise serializers.ValidationError("Terjadi Duplikat Category")
    return data
    
  