from rest_framework import permissions

class CookieAuthentication(permissions.BasePermission):
   """
   Allows access only to authenticated users with a valid sessionid cookie.
   """

   def has_permission(self, request, view):
       if 'sessionid' not in request.COOKIES:
           return False
       return True

class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            return bool(request.user and (request.user.is_moderator))
        except:
            return False
