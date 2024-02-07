from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

class CustomUserModelBackend(BaseBackend):
    def authenticate(self, request, login=None, password=None, **kwargs):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(login=login)
            if user.check_password(password):
                return user
        except user_model.DoesNotExist:
            return None
