from rest_framework import viewsets 
from ..models import Transaction 
from ..serializer import TransactionSerializer 
from ..filter_transaction import TransactionFilter


class TransactionAPI(viewsets.ModelViewSet):
  serializer_class = TransactionSerializer
  filterset_class = [TransactionFilter]

  def get_queryset(self):
    queryset = Transaction.objects.filter(user=self.request.user).select_related("category")
    return queryset

  def perform_create(self,serializer):
    serializer.save(user=self.request.user)