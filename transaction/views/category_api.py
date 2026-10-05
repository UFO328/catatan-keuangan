from rest_framework import viewsets 
from ..models import Category
from ..serializer import CategorySerializer 

class CategoryAPI(viewsets.ModelViewSet):
  serializer_class = CategorySerializer

  def get_queryset(self):
    queryset = Category.objects.select_related("user")
    return queryset

  def perform_create(self,serializer):
    serializer.save(user=self.request.user)