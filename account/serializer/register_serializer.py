from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from helper.default_category import create_default_categories

class RegisterSerializer(serializers.Serializer):
  """Serializer untuk registrasi user baru.

  Password diperiksa dengan password validator Django
  (panjang minimal, tidak mirip username, bukan password umum, dll).
  """
  username = serializers.CharField(
    max_length=150,
    help_text="Nama pengguna unik, maksimal 150 karakter.",
  )
  email = serializers.EmailField(
    help_text="Alamat email valid dan belum terdaftar.",
  )
  password = serializers.CharField(
    max_length=240,
    write_only=True,
    help_text="Password akun. Tidak pernah dikembalikan oleh API.",
  )

  class Meta:
    model = User
    fields = ["username","email","password"]

  def validate_password(self,pw):
    try:
      validate_password(pw)
    except ValidationError as e:
      raise serializers.ValidationError(list(e.message))
    return pw

  def validate(self,data):
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if User.objects.filter(username=username).exists():
      raise serializers.ValidationError({"username":"Username Tidak Tersedia"})

    if User.objects.filter(email=email).exists():
      raise serializers.ValidationError({"email":"email Tidak Tersedia"})

    return data

  def create(self,data):
    user = User.objects.create_user(
      username=data.get("username"),
      password=data.get("password"),
      email=data.get("email"),
    )
    create_default_categories(user)
    return user



