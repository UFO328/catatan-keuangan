from rest_framework import serializers 
from ..models import Category

class CategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Category
    fields = "__all__"
    read_only_fields=['user','created_at','updated_at']

  