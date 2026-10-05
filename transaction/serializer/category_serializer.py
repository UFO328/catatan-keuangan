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
