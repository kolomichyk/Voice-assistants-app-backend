from django.shortcuts import render
import redis
import json
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from voice_assistants_app.permissions import CookieAuthentication, IsModerator
from voice_assistants_app.serializers import ActionsSerializer, ApplicationsSerializer, ApplicationsActionsSerializer, UsersSerializer
from voice_assistants_app.models import Actions, Applications, NewUser, Users, ApplicationsActions
from rest_framework.decorators import api_view
from datetime import datetime
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes, authentication_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
import uuid

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class CurrentUserSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls._get_user()
        return cls._instance

    @classmethod
    def _get_user(cls):
        return Users.objects.get(login='testUser')


@api_view(['Get'])
def get_list(request, format=None):
    """
    Возвращает список услуг
    """
    print('get')
    actions = Actions.objects.all()
    serializer = ActionsSerializer(actions, many=True)
    print(request.user)
    return Response(serializer.data)

@swagger_auto_schema(method='post', request_body=ActionsSerializer)
@api_view(['Post'])
@permission_classes([IsModerator])
def post_list(request, format=None):    
    """
    Добавляет новую услугу
    """
    print('post')
    serializer = ActionsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='put', request_body=ActionsSerializer)
@permission_classes([IsModerator])
@api_view(['Put'])
def put_detail(request, pk, format=None):
    """
    Обновляет информацию об услуге
    """
    action = get_object_or_404(Actions, pk=pk)
    serializer = ActionsSerializer(action, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Get'])
def get_detail(request, pk, format=None):
    action = get_object_or_404(Actions, pk=pk)
    if request.method == 'GET':
        """
        Возвращает информацию об услуге
        """
        serializer = ActionsSerializer(action)
        return Response(serializer.data)

@api_view(['Delete'])
@permission_classes([IsModerator])
def delete_detail(request, pk, format=None):    
    """
    Удаляет информацию об услуге
    """
    action = get_object_or_404(Actions, pk=pk)
    action.delete()
    actions = Actions.objects.all()
    serializer = ActionsSerializer(actions, many=True)
    return Response(serializer.data)

@api_view(['Post'])
@permission_classes([IsAuthenticated])
def post_detail_to_application(request, pk, format=None):
    """
    Добавление заявки в услугу
    """
    try:
        ssid = request.COOKIES.get('sessionid')
        current_user = r.hgetall(ssid)

        application = None
        try: 
            application = Applications.objects.filter(customer_id=current_user['user_id'], status="черновик").latest('created_at')
        except:
            application = Applications(
                status = "черновик",
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                formed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                customer_id = current_user['user_id'],
                moderator_id = 1,
            )
            application.save()
        serializer = ApplicationsSerializer(application)

        action = Actions.objects.get(action_id=pk)
        try:
            applications_actions = ApplicationsActions.objects.get(application_id=application.application_id, action_id=action.action_id)
            return Response("Такое действие уже добавлено заявку")
        except ApplicationsActions.DoesNotExist:
            applications_actions = ApplicationsActions(
                application_id = application.application_id,
                action_id = action.action_id
            )
            applications_actions.save()
        
        application_action = ApplicationsActions.objects.filter(application_id=application.application_id)
        serializer = ApplicationsActionsSerializer(application_action, many=True)

        actions_id = list()
        for i in serializer.data:
            actions_id.append(i['action_id'])

        resp = []

        serializer = ApplicationsSerializer(application)
        resp.append(serializer.data)

        action_records = Actions.objects.all().filter(action_id__in=actions_id)
        serializer = ActionsSerializer(action_records, many=True)
        resp.append(serializer.data)

        return Response(resp)

    except:
        return Response("Error: there is no session")
    

@api_view(['Get'])
@permission_classes([IsAuthenticated])
def get_list_applications(request, format=None):
    """
    Возвращает список заявок
    """

    try:
        ssid = request.COOKIES.get('sessionid')
        current_user = r.hgetall(ssid)

        resp = []
        try:
            application = Applications.objects.filter(customer_id=current_user['user_id'], status="черновик").latest('created_at')
            
            serializer = ApplicationsSerializer(application)
            resp.append(serializer.data['application_id'])
        except:
            resp.append('Нет черновика')
        applications = Applications.objects.filter(customer_id=current_user['user_id'])
        serializer = ApplicationsSerializer(applications, many=True)
        resp.append(serializer.data)

        return Response(resp)
    except:
        return Response("Error: there is no session")

@api_view(['Get'])
@permission_classes([IsAuthenticated])
def get_detail_applications(request, pk, format=None):
    """
    Возвращает заявку с услугами
    """
    try:
        ssid = request.COOKIES.get('sessionid')
        current_user = r.hgetall(ssid)


        application = Applications.objects.filter(customer_id=current_user['user_id'], application_id=pk).latest('created_at')
        if not application:
            return Response("Заявки не существует")
        application_action = ApplicationsActions.objects.filter(application_id=application.application_id)
        serializer = ApplicationsActionsSerializer(application_action, many=True)

        actions_id = list()
        for i in serializer.data:
            actions_id.append(i['action_id'])

        resp = []

        serializer = ApplicationsSerializer(application)
        resp.append(serializer.data)

        action_records = Actions.objects.all().filter(action_id__in=actions_id)
        serializer = ActionsSerializer(action_records, many=True)
        resp.append(serializer.data)

        return Response(resp)
    
    except:
        return Response("Error: there is no session")
    
@api_view(['Put'])
@permission_classes([IsAuthenticated])
def put_detail_applications(request, pk, format=None):
    """
    Обновляет информацию о заявке
    """
    try:
        ssid = request.COOKIES.get('sessionid')
        current_user = r.hgetall(ssid)
        applications = get_object_or_404(Applications, pk=pk)
        serializer = ApplicationsSerializer(applications, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except:
        return Response("Error: there is no such application")
    
@api_view(['Delete'])
@permission_classes([IsAuthenticated])
def delete_detail_application(request, pk, format=None):    
    """
    Удаляет информацию о заявке
    """
    try:
        ssid = request.COOKIES.get('sessionid')
        current_user = r.hgetall(ssid)

        application = get_object_or_404(Applications, pk=pk)

        applications_action = ApplicationsActions.objects.all().filter(application_id=application.application_id)
        applications_action.delete()
        application.delete()
        applications = Applications.objects.all()
        serializer = ApplicationsSerializer(applications, many=True)
        return Response(serializer.data)
    
    except:
        return Response("Error: there is no such application")
    
@csrf_exempt
@swagger_auto_schema(method='put', request_body=ApplicationsSerializer)
@api_view(['Put'])
@permission_classes([IsModerator])
def put_detail_applications_moderator(request, pk, format=None):
    """
    Обновляет информацию о заявке
    """
    applications = get_object_or_404(Applications, pk=pk)
    serializer = ApplicationsSerializer(applications, data=request.data)
    if (applications.status == "проверяется" and (request.data['status'] == "отказано" or request.data['status'] == "принято")):
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response("Неверный статус заявки", status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@swagger_auto_schema(method='put', request_body=ApplicationsSerializer)
@api_view(['Put'])
@permission_classes([IsAuthenticated])
def put_detail_applications_user(request, pk, format=None):
    """
    Обновляет информацию о заявке
    """
    applications = get_object_or_404(Applications, pk=pk)
    serializer = ApplicationsSerializer(applications, data=request.data)
    # print(applications.application_id)
    if ((applications.status == "зарегистрирован" and request.data['status'] == "проверяется") or (applications.status == "черновик" and request.data['status'] == "зарегистрирован")):
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response("Неверный статус заявки", status=status.HTTP_400_BAD_REQUEST)

@api_view(['Delete'])
@permission_classes([IsAuthenticated])
def DeleteApplicationAction(request, pk):
    current_user = CurrentUserSingleton.get_instance()
    application = Applications.objects.filter(customer_id=current_user.user_id, status="зарегистрирован").latest('created_at')
    print(application.status)
    try:
        action = Actions.objects.get(action_id=pk, status='0')
        try:
            print(application.application_id, action.action_id)
            action_application = get_object_or_404(ApplicationsActions, application_id=application.application_id, action_id=action.action_id)
            action_application.delete()
            return Response("Действие удалено", status=200)
        except ApplicationsActions.DoesNotExist:
            return Response("Заявка не найдена", status=404)
    except Actions.DoesNotExist:
        return Response("Такого действия нет", status=400)
    
@csrf_exempt
@swagger_auto_schema(method='put', request_body=ApplicationsSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def PutApplicationActions(request, pk):
    current_user = CurrentUserSingleton.get_instance()
    application = Applications.objects.filter(customer_id=current_user.user_id, status="зарегистрирован").latest('created_at')
    action = Actions.objects.get(pk=pk, status='0')
    application_action = ApplicationsActions.objects.filter(application_id=application.application_id, action_id=action.action_id).first()
    print(application.application_id, action.action_id)
    if application_action and action:
        serializer = ApplicationsActionsSerializer(application_action, data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    else:
        return Response("Заявка не найдена", status=404)
    
# Статусы: ["Черновик", "Зарегистрирован", "Проверяется", "Отказано", "Принято", "Удалено"]

class UserViewSet(viewsets.ModelViewSet):
    """Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    model_class = Users

    def create(self, request):
        """
        Функция регистрации новых пользователей
        Если пользователя c указанным в request login ещё нет, то в БД будет добавлен новый пользователь.
        """
        if self.model_class.objects.filter(login=request.data['login']).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            self.model_class.objects.create_user(login=serializer.data['login'],
                                     password=serializer.data['password'],
                                     is_moderator=serializer.data['is_moderator'],
                                     fio=serializer.data['fio'])
            return Response({'status': 'Success'}, status=200)
        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@swagger_auto_schema(method='post', request_body=UsersSerializer)
@api_view(['Post'])
@permission_classes([AllowAny])
def login_view(request):
    print(1)
    username = request.data.get('login')
    password = request.data.get('password')
    user = authenticate(request, login=username, password=password)
    if user is not None:
        user = Users.objects.all().filter(login=user)
        serializer = UsersSerializer(user, many=True)

        user_data = {
            'user_id': serializer.data[0]['user_id'],
            'login': serializer.data[0]['login'],
            'password': serializer.data[0]['password'],
            'is_moderator': str(serializer.data[0]['is_moderator']),
            'fio': serializer.data[0]['fio']
        }

        random_key = str(uuid.uuid4())
        r.hset(f"{random_key}", mapping=user_data)

        response = HttpResponse(user_data, status=status.HTTP_201_CREATED)
        response.set_cookie("sessionid", random_key, samesite="Lax", max_age=30 * 24 * 60 * 60)
        return response
    else:
        # Вход не удался
        return HttpResponse({'message': f'Неверные учетные данные логин: {login}, пароль: {password}'}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(method='delete')
@api_view(['delete'])
@permission_classes([CookieAuthentication])
def logout_view(request):
    cookie_value = request.COOKIES.get('sessionid')
    print(cookie_value)
    r.delete(cookie_value)
    response = JsonResponse({'message': 'Успех!'})
    response.delete_cookie('sessionid')
    return response

class UserViewSet(viewsets.ModelViewSet):
    """Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    model_class = Users

    def create(self, request):
        """
        Функция регистрации новых пользователей
        Если пользователя c указанным в request email ещё нет, в БД будет добавлен новый пользователь.
        """
        if self.model_class.objects.filter(login=request.data['login']).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            self.model_class.objects.create_user(login=serializer.data['login'],
                                     password=serializer.data['password'],
                                     is_moderator=serializer.data['is_moderator'],
                                     fio=serializer.data['fio'])
            return Response({'status': 'Success'}, status=200)
        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)