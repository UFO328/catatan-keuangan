import django_filters
from .models import Transaction

class TransactionFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(
        queryset=lambda request: Category.objects.filter(user=request.user)
    )
    date_from = django_filters.DateFilter(field_name="transaction_date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="transaction_date", lookup_expr="lte")

    class Meta:
        model = Transaction
        fields = ["type", "category"]