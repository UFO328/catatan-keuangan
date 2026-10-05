from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class LoginSerializer(TokenObtainPairSerializer):
  """Serializer login.

  Mengembalikan access & refresh token JWT,
  ditambah klaim tambahan `username` dan `id` di dalam token
  serta di response JSON.
  """

  @classmethod
  def get_token(cls,user):
    token = super().get_token(user)

    token["username"] = user.username
    token["id"] = user.id

    return token

  def validate(self,attrs):
    data = super().validate(attrs)

    data["username"] = self.user.username
    data["id"] = self.user.id
    return data
