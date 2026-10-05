from rest_framework.routers import DefaultRouter 
from .views import TransactionAPI,CategoryAPI

router = DefaultRouter()
router.register("transaction",TransactionAPI,basename="transaction")
router.register("category",CategoryAPI,basename="Category")

urlpatterns = router.urls