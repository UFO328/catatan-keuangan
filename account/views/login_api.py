from rest_framework_simplejwt.views import TokenObtainPairView 
from ..serializer import LoginSerializer 

class LoginAPI(TokenObtainPairView):
  serializer_class = LoginSerializer