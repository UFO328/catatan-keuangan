from rest_framework import serializers 
from django.contrib.auth.models import User 
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from helper.default_category import create_default_categories
class RegisterSerializer(serializers.Serializer):
  username = serializers.CharField(max_length=150)
  email = serializers.EmailField()
  password = serializers.CharField(max_length=240,write_only=True)
  
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

    

    