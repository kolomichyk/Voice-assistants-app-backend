from django.contrib import admin
from django.urls import path
from django.contrib import admin
from voice_assistants_app import views
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'actions/', views.get_list, name='actions-list'),
    path(r'actions/post/', views.post_list, name='actions-post'),
    path(r'actions/<int:pk>/', views.get_detail, name='actions-detail'),
    path(r'actions/<int:pk>/put/', views.put_detail, name='actions-put'),
    path(r'actions/<int:pk>/delete/', views.delete_detail, name='actions-delete'),
    path(r'actions/<int:pk>/put/application/<int:application_id>', views.put_detail_to_application, name='actions-put-to-application'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path(r'applications/', views.get_list_applications, name='applications-list'),
    path(r'applications/<int:pk>/', views.get_detail_applications, name='applications-detail'),
    path(r'applications/<int:pk>/put/', views.put_detail_applications, name='applications-put'),
    path(r'applications/<int:pk>/delete/', views.delete_detail_application, name='applications-delete'),
    path(r'applications/<int:pk>/put/moderator/', views.put_detail_applications_moderator, name='applications-put-moderator'),
    path(r'applications/<int:pk>/put/user/', views.put_detail_applications_user, name='applications-put-user'),
    path('admin/', admin.site.urls),
]
