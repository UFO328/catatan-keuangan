from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from transaction.models import Category

REGISTER_URL = "/auth/catatan_keuangan/api/register/"
LOGIN_URL = "/auth/catatan_keuangan/api/login/"

EXPECTED_DEFAULT_CATEGORIES = sorted(
  [
    "Makan",
    "Transportasi",
    "Belanja",
    "Tagihan",
    "Hiburan",
    "Uang Saku",
    "Lainnya",
  ]
)


class RegisterAPITestCase(TestCase):
  def setUp(self):
    self.client = APIClient()
    self.payload = {
      "username": "userbaru",
      "email": "userbaru@example.com",
      "password": "SuperKuat2026!",
    }

  def test_register_success_creates_user_and_default_categories(self):
    res = self.client.post(REGISTER_URL, self.payload, format="json")
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    self.assertEqual(res.data, {"message": "Account Berhasil Dibuat"})
    user = User.objects.get(username="userbaru")
    self.assertTrue(user.check_password("SuperKuat2026!"))
    self.assertEqual(user.categories.count(), 7)
    self.assertEqual(
      sorted(user.categories.values_list("name", flat=True)),
      EXPECTED_DEFAULT_CATEGORIES,
    )
    self.assertTrue(all(user.categories.values_list("is_default", flat=True)))

  def test_register_duplicate_username_rejected(self):
    User.objects.create_user(username="userbaru", password="SuperKuat2026!")
    res = self.client.post(REGISTER_URL, self.payload, format="json")
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertIn("username", res.data)

  def test_register_duplicate_email_rejected_with_correct_key(self):
    User.objects.create_user(
      username="lain", email="userbaru@example.com", password="SuperKuat2026!"
    )
    res = self.client.post(REGISTER_URL, self.payload, format="json")
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertIn("email", res.data)

  def _post_without_crash(self, payload):
    client = APIClient(raise_request_exception=False)
    return client.post(REGISTER_URL, payload, format="json")

  def test_register_weak_password_rejected(self):
    self.payload["password"] = "123"
    res = self._post_without_crash(self.payload)
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_register_common_password_rejected(self):
    self.payload["password"] = "password"
    res = self._post_without_crash(self.payload)
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_register_numeric_password_rejected(self):
    self.payload["password"] = "1234567890"
    res = self._post_without_crash(self.payload)
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_register_missing_username_rejected(self):
    del self.payload["username"]
    res = self.client.post(REGISTER_URL, self.payload, format="json")
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_register_missing_email_rejected(self):
    del self.payload["email"]
    res = self.client.post(REGISTER_URL, self.payload, format="json")
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_register_missing_password_rejected(self):
    del self.payload["password"]
    res = self.client.post(REGISTER_URL, self.payload, format="json")
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_register_invalid_email_format_rejected(self):
    self.payload["email"] = "bukan-email"
    res = self.client.post(REGISTER_URL, self.payload, format="json")
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_register_get_method_not_allowed(self):
    res = self.client.get(REGISTER_URL)
    self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class LoginAPITestCase(TestCase):
  def setUp(self):
    self.client = APIClient()
    self.user = User.objects.create_user(
      username="loginuser",
      email="login@example.com",
      password="SuperKuat2026!",
    )

  def test_login_success_returns_tokens_and_user_info(self):
    res = self.client.post(
      LOGIN_URL,
      {"username": "loginuser", "password": "SuperKuat2026!"},
      format="json",
    )
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertIn("access", res.data)
    self.assertIn("refresh", res.data)
    self.assertEqual(res.data["username"], "loginuser")
    self.assertEqual(res.data["id"], self.user.id)

  def test_login_wrong_password_rejected(self):
    res = self.client.post(
      LOGIN_URL,
      {"username": "loginuser", "password": "salah"},
      format="json",
    )
    self.assertIn(
      res.status_code,
      [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED],
    )

  def test_login_unknown_user_rejected(self):
    res = self.client.post(
      LOGIN_URL,
      {"username": "tidakada", "password": "SuperKuat2026!"},
      format="json",
    )
    self.assertIn(
      res.status_code,
      [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED],
    )

  def test_login_missing_password_rejected(self):
    res = self.client.post(
      LOGIN_URL, {"username": "loginuser"}, format="json"
    )
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_login_get_method_not_allowed(self):
    res = self.client.get(LOGIN_URL)
    self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
