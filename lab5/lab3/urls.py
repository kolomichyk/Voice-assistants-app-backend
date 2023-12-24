from django.contrib import admin
from voice_assistants_app import views
from rest_framework import routers
from rest_framework import permissions
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


router = routers.DefaultRouter()

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router.register(r'user', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path(r'actions/', views.get_list, name='actions_list'), # +
    path(r'actions/post/', views.post_list, name='actions_post'), # +
    path(r'actions/<int:pk>/', views.get_detail, name='actions_detail'), # +
    path(r'actions/put/<int:pk>/', views.put_detail, name='actions_put'), # +
    path(r'actions/delete/<int:pk>/', views.delete_detail, name='actions_delete'), # +
    path(r'actions/post/application/<int:pk>/', views.post_detail_to_application, name='actions_put_to_application'), # +

    path(r'applications/', views.get_list_applications, name='applications_list'), # +
    path(r'applications/<int:pk>/', views.get_detail_applications, name='applications_detail'), # +
    path(r'applications/put/<int:pk>/', views.put_detail_applications, name='applications_put'),  # +
    path(r'applications/delete/<int:pk>/', views.delete_detail_application, name='applications_delete'),
    path(r'applications/put/moderator/<int:pk>/', views.put_detail_applications_moderator, name='applications_put_moderator'), # +
    path(r'applications/put/user/<int:pk>/', views.put_detail_applications_user, name='applications_put_user'), # +

    path(r'actions/applications/delete/<int:pk>/', views.DeleteApplicationAction, name = 'application_action_delete'), # +
    path(r'actions/applications/put/<int:pk>/', views.PutApplicationActions, name = 'application_action_put'), # +
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

   
    # path(r'user', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

   #  path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login/',  views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('admin/', admin.site.urls),
]
