from rest_framework import permissions
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
class CookieAuthentication(permissions.BasePermission):
   """
   Allows access only to authenticated users with a valid sessionid cookie.
   """

   def has_permission(self, request, view):
       if 'auth' not in request.COOKIES:
           return False
       return True

class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            ssid = request.COOKIES.get('auth')
            current_user = r.hgetall(ssid)
            return bool((current_user['is_moderator']))
        except:
            return False
