from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from helper.default_category import create_default_categories
from transaction.models import Category, Transaction

LOGIN_URL = "/auth/catatan_keuangan/api/login/"
CATEGORY_URL = "/transaction/catatan_keuangan/api/category/"
TRANSACTION_URL = "/transaction/catatan_keuangan/api/transaction/"
DASHBOARD_URLS = [
  "/transaction/catatan_keuangan/api/dashboard/",
  "/transaction/catatan_keuangan/api/transaction/aggregation/",
  "/transaction/catatan_keuangan/api/summary/",
]


class BaseTestCase(TestCase):
  def setUp(self):
    self.user1 = User.objects.create_user(
      username="user1", email="u1@example.com", password="PassKuat2026!"
    )
    self.user2 = User.objects.create_user(
      username="user2", email="u2@example.com", password="PassKuat2026!"
    )
    create_default_categories(self.user1)
    create_default_categories(self.user2)
    self.token1 = self._login("user1")
    self.token2 = self._login("user2")
    self.client1 = APIClient()
    self.client1.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token1}")
    self.client2 = APIClient()
    self.client2.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token2}")
    self.anon = APIClient()
    self.category1 = self.user1.categories.first()
    self.category2 = self.user2.categories.first()

  def _login(self, username):
    res = APIClient().post(
      LOGIN_URL,
      {"username": username, "password": "PassKuat2026!"},
      format="json",
    )
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    return res.data["access"]

  def tx_payload(self, **overrides):
    payload = {
      "user": self.user1.id,
      "category": self.category1.id,
      "type": "EXPENSE",
      "amount": "1000.00",
      "description": "makan siang",
      "transaction_date": "2026-01-15T10:30:00Z",
    }
    payload.update(overrides)
    return payload


class AuthenticationTestCase(BaseTestCase):
  def test_category_list_requires_login(self):
    res = self.anon.get(CATEGORY_URL)
    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

  def test_category_detail_requires_login(self):
    res = self.anon.get(f"{CATEGORY_URL}{self.category1.pk}/")
    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

  def test_transaction_list_requires_login(self):
    res = self.anon.get(TRANSACTION_URL)
    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

  def test_transaction_create_requires_login(self):
    res = self.anon.post(TRANSACTION_URL, self.tx_payload(), format="json")
    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

  def test_invalid_token_rejected(self):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer token.tidak.valid")
    res = client.get(TRANSACTION_URL)
    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

  def test_malformed_authorization_header_rejected(self):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=self.token1)
    res = client.get(TRANSACTION_URL)
    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class CategoryCRUDTestCase(BaseTestCase):
  def test_list_returns_own_default_categories(self):
    res = self.client1.get(CATEGORY_URL)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data["count"], 7)

  def test_create_category(self):
    res = self.client1.post(
      CATEGORY_URL,
      {"user": self.user1.id, "name": "Hadiah"},
      format="json",
    )
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    cat = Category.objects.get(user=self.user1, name="Hadiah")
    self.assertEqual(res.data["id"], cat.pk)
    self.assertEqual(res.data["name"], "Hadiah")
    self.assertFalse(res.data["is_default"])

  def test_create_category_user_assigned_automatically_from_token(self):
    res = self.client1.post(CATEGORY_URL, {"name": "Hadiah"}, format="json")
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    self.assertTrue(Category.objects.filter(user=self.user1, name="Hadiah").exists())

  def test_retrieve_own_category(self):
    cat = Category.objects.create(user=self.user1, name="Rahasia")
    res = self.client1.get(f"{CATEGORY_URL}{cat.pk}/")
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data["name"], "Rahasia")

  def test_update_own_category(self):
    cat = Category.objects.create(user=self.user1, name="Rahasia")
    payload = {"user": self.user1.id, "name": "Baru", "is_default": False}
    res = self.client1.put(f"{CATEGORY_URL}{cat.pk}/", payload, format="json")
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    cat.refresh_from_db()
    self.assertEqual(cat.name, "Baru")

  def test_partial_update_own_category(self):
    cat = Category.objects.create(user=self.user1, name="Rahasia")
    res = self.client1.patch(
      f"{CATEGORY_URL}{cat.pk}/", {"name": "Diubah"}, format="json"
    )
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    cat.refresh_from_db()
    self.assertEqual(cat.name, "Diubah")

  def test_delete_own_category(self):
    cat = Category.objects.create(user=self.user1, name="Rahasia")
    res = self.client1.delete(f"{CATEGORY_URL}{cat.pk}/")
    self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
    self.assertFalse(Category.objects.filter(pk=cat.pk).exists())


class CategoryValidationTestCase(BaseTestCase):
  def test_create_category_empty_name_rejected(self):
    res = self.client1.post(CATEGORY_URL, {"name": ""}, format="json")
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_create_category_missing_name_rejected(self):
    res = self.client1.post(CATEGORY_URL, {}, format="json")
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_duplicate_category_name_same_user_returns_400(self):
    client = APIClient(raise_request_exception=False)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token1}")
    res = client.post(
      CATEGORY_URL,
      {"user": self.user1.id, "name": self.category1.name},
      format="json",
    )
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_duplicate_category_name_same_user_db_constraint_exists(self):
    Category.objects.create(user=self.user1, name="Duplikat")
    with self.assertRaises(IntegrityError):
      Category.objects.create(user=self.user1, name="Duplikat")

  def test_same_category_name_different_users_allowed(self):
    res1 = self.client1.post(
      CATEGORY_URL, {"user": self.user1.id, "name": "Hadiah"}, format="json"
    )
    self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
    res2 = self.client2.post(
      CATEGORY_URL, {"user": self.user2.id, "name": "Hadiah"}, format="json"
    )
    self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
    self.assertEqual(Category.objects.filter(name="Hadiah").count(), 2)


class CategoryIsolationTestCase(BaseTestCase):
  def test_list_does_not_leak_other_users_categories(self):
    Category.objects.create(user=self.user1, name="RahasiaUser1")
    res = self.client2.get(CATEGORY_URL)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data["count"], 7)

  def test_retrieve_other_users_category_rejected(self):
    cat = Category.objects.create(user=self.user1, name="RahasiaUser1")
    res = self.client2.get(f"{CATEGORY_URL}{cat.pk}/")
    self.assertIn(res.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

  def test_update_other_users_category_rejected(self):
    cat = Category.objects.create(user=self.user1, name="RahasiaUser1")
    res = self.client2.patch(
      f"{CATEGORY_URL}{cat.pk}/", {"name": "Ubah"}, format="json"
    )
    self.assertIn(res.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    cat.refresh_from_db()
    self.assertEqual(cat.name, "RahasiaUser1")

  def test_delete_other_users_category_rejected(self):
    cat = Category.objects.create(user=self.user1, name="RahasiaUser1")
    res = self.client2.delete(f"{CATEGORY_URL}{cat.pk}/")
    self.assertIn(res.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    self.assertTrue(Category.objects.filter(pk=cat.pk).exists())

  def test_create_category_for_other_user_rejected(self):
    res = self.client1.post(
      CATEGORY_URL, {"name": "Titipan", "user": self.user2.id}, format="json"
    )
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertFalse(Category.objects.filter(user=self.user2, name="Titipan").exists())

  def test_update_cannot_reassign_category_to_other_user(self):
    cat = Category.objects.create(user=self.user1, name="RahasiaUser1")
    res = self.client1.patch(
      f"{CATEGORY_URL}{cat.pk}/", {"user": self.user2.id}, format="json"
    )
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    cat.refresh_from_db()
    self.assertEqual(cat.user, self.user1)


class TransactionCRUDTestCase(BaseTestCase):
  def test_create_transaction(self):
    res = self.client1.post(TRANSACTION_URL, self.tx_payload(), format="json")
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    tx = Transaction.objects.get(user=self.user1, amount=Decimal("1000.00"))
    self.assertEqual(tx.type, "EXPENSE")
    self.assertEqual(tx.category, self.category1)
    self.assertEqual(tx.description, "makan siang")

  def test_create_transaction_user_assigned_automatically_from_token(self):
    payload = self.tx_payload()
    del payload["user"]
    res = self.client1.post(TRANSACTION_URL, payload, format="json")
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    self.assertTrue(
      Transaction.objects.filter(user=self.user1, amount=Decimal("1000.00")).exists()
    )

  def test_list_returns_own_transactions(self):
    Transaction.objects.create(
      user=self.user1, category=self.category1, type="EXPENSE",
      amount="1000.00", transaction_date="2026-01-15T10:30:00Z",
    )
    Transaction.objects.create(
      user=self.user2, category=self.category2, type="INCOME",
      amount="2000.00", transaction_date="2026-01-15T11:30:00Z",
    )
    res = self.client1.get(TRANSACTION_URL)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data["count"], 1)

  def test_retrieve_own_transaction(self):
    tx = Transaction.objects.create(
      user=self.user1, category=self.category1, type="EXPENSE",
      amount="1000.00", transaction_date="2026-01-15T10:30:00Z",
    )
    res = self.client1.get(f"{TRANSACTION_URL}{tx.pk}/")
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(str(res.data["amount"]), "1000.00")

  def test_update_own_transaction(self):
    tx = Transaction.objects.create(
      user=self.user1, category=self.category1, type="EXPENSE",
      amount="1000.00", transaction_date="2026-01-15T10:30:00Z",
    )
    payload = {
      "user": self.user1.id,
      "category": self.category1.id,
      "type": "INCOME",
      "amount": "25000.00",
      "description": "diubah",
      "transaction_date": "2026-02-01T09:00:00Z",
    }
    res = self.client1.put(f"{TRANSACTION_URL}{tx.pk}/", payload, format="json")
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    tx.refresh_from_db()
    self.assertEqual(tx.type, "INCOME")
    self.assertEqual(str(tx.amount), "25000.00")

  def test_partial_update_own_transaction(self):
    tx = Transaction.objects.create(
      user=self.user1, category=self.category1, type="EXPENSE",
      amount="1000.00", transaction_date="2026-01-15T10:30:00Z",
    )
    res = self.client1.patch(
      f"{TRANSACTION_URL}{tx.pk}/", {"description": "ganti deskripsi"}, format="json"
    )
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    tx.refresh_from_db()
    self.assertEqual(tx.description, "ganti deskripsi")

  def test_delete_own_transaction(self):
    tx = Transaction.objects.create(
      user=self.user1, category=self.category1, type="EXPENSE",
      amount="1000.00", transaction_date="2026-01-15T10:30:00Z",
    )
    res = self.client1.delete(f"{TRANSACTION_URL}{tx.pk}/")
    self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
    self.assertFalse(Transaction.objects.filter(pk=tx.pk).exists())

  def test_list_empty_returns_zero(self):
    res = self.client1.get(TRANSACTION_URL)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data["count"], 0)


class TransactionValidationTestCase(BaseTestCase):
  def test_amount_zero_rejected(self):
    res = self.client1.post(
      TRANSACTION_URL, self.tx_payload(amount="0.00"), format="json"
    )
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_amount_negative_rejected(self):
    res = self.client1.post(
      TRANSACTION_URL, self.tx_payload(amount="-5000.00"), format="json"
    )
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_amount_non_numeric_rejected(self):
    res = self.client1.post(
      TRANSACTION_URL, self.tx_payload(amount="abc"), format="json"
    )
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_amount_exceeding_max_digits_rejected(self):
    res = self.client1.post(
      TRANSACTION_URL, self.tx_payload(amount="99999999999999.00"), format="json"
    )
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_type_must_be_income_or_expense(self):
    res = self.client1.post(
      TRANSACTION_URL, self.tx_payload(type="TRANSFER"), format="json"
    )
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_type_missing_rejected(self):
    payload = self.tx_payload()
    del payload["type"]
    res = self.client1.post(TRANSACTION_URL, payload, format="json")
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_category_missing_rejected(self):
    payload = self.tx_payload()
    del payload["category"]
    res = self.client1.post(TRANSACTION_URL, payload, format="json")
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_category_nonexistent_rejected(self):
    res = self.client1.post(
      TRANSACTION_URL, self.tx_payload(category=999999), format="json"
    )
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_category_from_other_user_rejected(self):
    res = self.client1.post(
      TRANSACTION_URL, self.tx_payload(category=self.category2.id), format="json"
    )
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertFalse(
      Transaction.objects.filter(user=self.user1, category=self.category2).exists()
    )

  def test_transaction_date_missing_rejected(self):
    payload = self.tx_payload()
    del payload["transaction_date"]
    res = self.client1.post(TRANSACTION_URL, payload, format="json")
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_transaction_date_invalid_format_rejected(self):
    res = self.client1.post(
      TRANSACTION_URL,
      self.tx_payload(transaction_date="15-Januari-2026"),
      format="json",
    )
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_transaction_date_valid_future_date_accepted(self):
    res = self.client1.post(
      TRANSACTION_URL,
      self.tx_payload(transaction_date="2030-12-31T23:59:59Z"),
      format="json",
    )
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

  def test_transaction_date_valid_past_date_accepted(self):
    res = self.client1.post(
      TRANSACTION_URL,
      self.tx_payload(transaction_date="2020-01-01T00:00:00Z"),
      format="json",
    )
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

  def test_description_optional(self):
    payload = self.tx_payload()
    del payload["description"]
    res = self.client1.post(TRANSACTION_URL, payload, format="json")
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

  def test_create_transaction_for_other_user_rejected(self):
    res = self.client1.post(
      TRANSACTION_URL, self.tx_payload(user=self.user2.id), format="json"
    )
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertFalse(
      Transaction.objects.filter(user=self.user2, amount=Decimal("1000.00")).exists()
    )


class TransactionIsolationTestCase(BaseTestCase):
  def setUp(self):
    super().setUp()
    self.tx1 = Transaction.objects.create(
      user=self.user1, category=self.category1, type="EXPENSE",
      amount="5000.00", description="milik user1",
      transaction_date="2026-01-10T08:00:00Z",
    )

  def test_list_does_not_leak_other_users_transactions(self):
    res = self.client2.get(TRANSACTION_URL)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data["count"], 0)

  def test_retrieve_other_users_transaction_rejected(self):
    res = self.client2.get(f"{TRANSACTION_URL}{self.tx1.pk}/")
    self.assertIn(res.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

  def test_update_other_users_transaction_rejected(self):
    payload = {
      "user": self.user1.id,
      "category": self.category1.id,
      "type": "INCOME",
      "amount": "1.00",
      "transaction_date": "2026-01-11T08:00:00Z",
    }
    res = self.client2.put(
      f"{TRANSACTION_URL}{self.tx1.pk}/", payload, format="json"
    )
    self.assertIn(res.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    self.tx1.refresh_from_db()
    self.assertEqual(str(self.tx1.amount), "5000.00")

  def test_delete_other_users_transaction_rejected(self):
    res = self.client2.delete(f"{TRANSACTION_URL}{self.tx1.pk}/")
    self.assertIn(res.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    self.assertTrue(Transaction.objects.filter(pk=self.tx1.pk).exists())


class TransactionListBehaviorTestCase(BaseTestCase):
  def _create_tx(self, amount, date):
    Transaction.objects.create(
      user=self.user1, category=self.category1, type="EXPENSE",
      amount=amount, transaction_date=date,
    )

  def test_pagination_applied_with_page_size_10(self):
    for i in range(12):
      self._create_tx(f"{i + 1}.00", f"2026-01-{i + 1:02d}T00:00:00Z")
    res = self.client1.get(TRANSACTION_URL)
    self.assertEqual(res.data["count"], 12)
    self.assertEqual(len(res.data["results"]), 10)
    self.assertIsNotNone(res.data["next"])
    self.assertIsNone(res.data["previous"])

  def test_list_ordered_by_transaction_date_desc(self):
    self._create_tx("1.00", "2026-01-01T00:00:00Z")
    self._create_tx("2.00", "2026-03-01T00:00:00Z")
    self._create_tx("3.00", "2026-02-01T00:00:00Z")
    res = self.client1.get(TRANSACTION_URL)
    dates = [item["transaction_date"] for item in res.data["results"]]
    self.assertEqual(
      dates,
      ["2026-03-01T00:00:00Z", "2026-02-01T00:00:00Z", "2026-01-01T00:00:00Z"],
    )

  def test_query_param_filtering_applied(self):
    self._create_tx("1.00", "2026-01-01T00:00:00Z")
    tx_income = Transaction.objects.create(
      user=self.user1, category=self.category1, type="INCOME",
      amount="2.00", transaction_date="2026-01-02T00:00:00Z",
    )
    res = self.client1.get(f"{TRANSACTION_URL}?type=INCOME")
    self.assertEqual(res.data["count"], 1)
    self.assertEqual(res.data["results"][0]["id"], tx_income.pk)


class DashboardEndpointTestCase(BaseTestCase):
  def test_aggregation_dashboard_endpoints_not_implemented(self):
    for url in DASHBOARD_URLS:
      res = self.client1.get(url)
      self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class ErrorHandlingTestCase(BaseTestCase):
  def test_get_nonexistent_transaction_returns_404(self):
    res = self.client1.get(f"{TRANSACTION_URL}999999/")
    self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

  def test_update_nonexistent_transaction_returns_404(self):
    res = self.client1.patch(
      f"{TRANSACTION_URL}999999/", {"description": "x"}, format="json"
    )
    self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

  def test_delete_nonexistent_transaction_returns_404(self):
    res = self.client1.delete(f"{TRANSACTION_URL}999999/")
    self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

  def test_get_nonexistent_category_returns_404(self):
    res = self.client1.get(f"{CATEGORY_URL}999999/")
    self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

  def test_delete_nonexistent_category_returns_404(self):
    res = self.client1.delete(f"{CATEGORY_URL}999999/")
    self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
