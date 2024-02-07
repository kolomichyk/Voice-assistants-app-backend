from django.shortcuts import render
import redis
import json
import requests
from django.http import HttpResponseBadRequest
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
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes, authentication_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
import uuid
from minio import Minio
from django.http import HttpResponseServerError
from datetime import timedelta
import time
from django.db.models import Q

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
    resp_data = []
    search = request.query_params.get('search', None)
    time.sleep(0.2)
    try:
        ssid = request.COOKIES.get('auth')
        current_user = r.hgetall(ssid)
        draft = Applications.objects.filter(customer_id=current_user['user_id'], status="черновик").latest('created_at')
        if not draft:
            resp_data.append({"draft_id": -1})
        else:
            serializer = ApplicationsSerializer(draft)
            resp_data.append({"draft_id": serializer.data['application_id']})  
    except:
        resp_data.append({"draft_id": -1})

    actions = None
    try:
        ssid = request.COOKIES.get('auth')
        current_user = r.hgetall(ssid)
        if (current_user['is_moderator']):
            if search is not None:
                actions = Actions.objects.filter(Q(title__icontains=search))
            else:
                actions = Actions.objects.all()
    except:
        if search is not None:
                actions = Actions.objects.filter(Q(title__icontains=search), status=0)
        else:
            actions = Actions.objects.filter(status=0)

    serializer = ActionsSerializer(actions, many=True)
    resp_data.append(serializer.data)
    response = HttpResponse(resp_data, status=status.HTTP_200_OK)
    return Response(resp_data, status=status.HTTP_200_OK)


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
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsModerator])
def postImageToAction(request, pk):
    if 'file' in request.FILES:
        print(request.FILES)
        print(pk)
        file = request.FILES['file']
        action = get_object_or_404(Actions, pk=pk)
        
        client = Minio(endpoint="localhost:9000",
                       access_key='ix7DSsEXReN4BXq000Xz',
                       secret_key='G2dvtMHiaxEwCwQyny9OIoBpiAJhlo7bCM0O1cVL',
                       secure=False)
        print(len(client.list_buckets()))

        bucket_name = 'actionsimages'
        file_name = file.name
        file_path = "http://localhost:9000/actionsimages/" + file_name
        
        try:
            client.put_object(bucket_name, file_name, file, length=file.size, content_type=file.content_type)
            print("Файл успешно загружен в Minio.")
            
            serializer = ActionsSerializer(instance=action, data={'img': file_path}, partial=True)
            if serializer.is_valid():
                serializer.save()
                print(file_path)
                return HttpResponse(file_path)
            else:
                return HttpResponseBadRequest('Invalid data.')
        except Exception as e:
            serializer = ActionsSerializer(instance=action, data={'img': file_path}, partial=True)
            if serializer.is_valid():
                serializer.save()
                print(file_path)
                return HttpResponse(file_path)
            else:
                return HttpResponseBadRequest('Invalid data.')

    return HttpResponseBadRequest('Invalid request.')

@swagger_auto_schema(method='put', request_body=ActionsSerializer)
@api_view(['Put'])
@permission_classes([IsModerator])
def put_detail(request, pk, format=None):
    """
    Обновляет информацию об услуге
    """
    print(request.data)
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
    serializer = ActionsSerializer(instance=action, data={'status': 1}, partial=True)
    if serializer.is_valid():
        serializer.save()
    actions = Actions.objects.all()
    serializer = ActionsSerializer(actions, many=True)
    return Response(serializer.data)

@api_view(['Post'])
@permission_classes([CookieAuthentication])
def post_detail_to_application(request, pk, format=None):
    """
    Добавление услуги в заявку
    """
    try:
        ssid = request.COOKIES.get('auth')
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
                action_id = action.action_id,
                description=action.title
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

        print(resp)
        return Response(resp)

    except:
        return Response("Error: there is no application")
    

@api_view(['Get'])
@permission_classes([CookieAuthentication])
def get_list_applications(request, format=None):
    """
    Возвращает список заявок
    """
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    status = request.GET.get('status')
    print(status)
    try:
        ssid = request.COOKIES.get('auth')
        current_user = r.hgetall(ssid)
        resp = []
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
            end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%fZ")
            if (current_user['is_moderator'] == "True"):
                applications = Applications.objects.filter()
                if start_date is not None and end_date is not None:
                    if status != 'Все':
                        applications = applications.filter(created_at__range=(start_date, end_date), status=status)
                    else:
                        applications = applications.filter(created_at__range=(start_date, end_date))
                        applications = applications.exclude(status="черновик")
            else:
                applications = Applications.objects.filter(customer_id=current_user['user_id'])
                if start_date is not None and end_date is not None:
                    if status != 'Все':
                        applications = applications.filter(created_at__range=(start_date, end_date), status=status)
                    else:
                        applications = applications.filter(created_at__range=(start_date, end_date))
                        applications = applications.exclude(status="черновик")

            serializer = ApplicationsSerializer(applications, many=True)
            resp.append(serializer.data)
        except Exception as e:
            print(e)
            resp.append([])
        users = Users.objects.all()
        users = UsersSerializer(users, many=True)
        for i in range(len(resp[0])):
            for j in range(len(users.data)):
                if (resp[0][i]['customer_id'] == users.data[j]['user_id']):
                    resp[0][i]['customer_id'] = users.data[j]['fio']
        
        return Response(resp)
    except:
        return Response("Error: there is no session")


@api_view(['Get'])
@permission_classes([CookieAuthentication])
def get_detail_applications(request, pk, format=None):
    """
    Возвращает заявку с услугами
    """
    try:
        ssid = request.COOKIES.get('auth')
        current_user = r.hgetall(ssid)
        application = Applications.objects.filter(application_id=pk).latest('created_at')
        if not application:
            return Response([-1])
        resp = []

        serializer = ApplicationsSerializer(application)
        resp.append(serializer.data)

        application_action = ApplicationsActions.objects.filter(application_id=application.application_id)
        serializer = ApplicationsActionsSerializer(application_action, many=True)

        resp.append(serializer.data)

        return Response(resp)
    
    except:
        return Response("Error: there is no session")

@api_view(['Get'])
@permission_classes([CookieAuthentication])
def get_detail_applications_list_actions(request, pk, format=None):
    """
    Возвращает заявку с услугами
    """
    try:
        ssid = request.COOKIES.get('auth')
        current_user = r.hgetall(ssid)

        application = Applications.objects.filter(application_id=pk).latest('created_at')
        if not application:
            return Response([-1])
        resp = []

        serializer = ApplicationsSerializer(application)
        resp.append(serializer.data)

        application_action = ApplicationsActions.objects.filter(application_id=serializer.data['application_id'])
        serializer = ApplicationsActionsSerializer(application_action, many=True)

        actions_id = list()
        for i in serializer.data:
            actions_id.append(i['action'])

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
@permission_classes([CookieAuthentication])
def delete_detail_from_application(request, pk, format=None):    
    """
    Удаляет информацию о заявке
    """
    try:
        ssid = request.COOKIES.get('auth')
        current_user = r.hgetall(ssid)

        application = Applications.objects.filter(customer_id=current_user['user_id'], status="черновик").latest('created_at')

        applications_action = ApplicationsActions.objects.all().filter(action_id=pk, application_id=application.application_id)
        applications_action.delete()
        if not ApplicationsActions.objects.all().filter(application_id=application.application_id):
            application.delete()
        
        application = Applications.objects.filter(customer_id=current_user['user_id'], status="черновик").latest('created_at')
        if not application:
            return Response([{"draft_id" : -1}])
        resp = []

        serializer = ApplicationsSerializer(application)
        resp.append(serializer.data)

        application_action = ApplicationsActions.objects.filter(application_id=application.application_id)
        serializer = ApplicationsActionsSerializer(application_action, many=True)

        resp.append(serializer.data)

        print(resp)
        return Response(resp)
    
    except:
        return Response("Error: there is no such application")

@api_view(['Post'])
@permission_classes([CookieAuthentication])
def delete_application(request, pk, format=None):    
    """
    Удаляет информацию о заявке
    """
    try:
        ssid = request.COOKIES.get('auth')
        current_user = r.hgetall(ssid)

        application = Applications.objects.filter(application_id=pk)

        applications_action = ApplicationsActions.objects.all().filter(application_id=pk)
        applications_action.delete()
        application.delete()
        
        return Response(status=status.HTTP_200_OK)
    
    except:
        return Response("Error: there is no such application")
    
@csrf_exempt
@swagger_auto_schema(method='put', request_body=ApplicationsSerializer)
@api_view(['Put'])
@permission_classes([IsModerator])
def put_detail_applications_moderator(request, format=None):
    """
    Обновляет информацию о заявке
    """
    ssid = request.COOKIES.get('auth')
    current_user = r.hgetall(ssid)
    request.data['moderator_id'] = current_user['user_id']
    print(request.data)
    applications = get_object_or_404(Applications, pk=request.data['application_id'])
    serializer = ApplicationsSerializer(applications, data=request.data)
    if (applications.status == "зарегистрирован" and (request.data['status'] == "отказано" or request.data['status'] == "принято")):
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response("Неверный статус заявки", status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@swagger_auto_schema(method='put', request_body=ApplicationsSerializer)
@api_view(['put'])
@permission_classes([CookieAuthentication])
def put_detail_applications_user(request, format=None):
    """
    Обновляет информацию о заявке
    """
    ssid = request.COOKIES.get('auth')
    current_user = r.hgetall(ssid)
    print(request.data)
    application = Applications.objects.filter(customer_id=current_user['user_id'], status="черновик").latest('created_at')
    serializer = ApplicationsSerializer(application, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(status=status.HTTP_200_OK)

    # applications = get_object_or_404(Applications)
    # serializer = ApplicationsSerializer(applications, data=request.data)
    # # print(applications.application_id)
    # if (applications.status == "черновик" and request.data['status'] == "зарегистрирован"):
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     return Response("Неверный статус заявки", status=status.HTTP_400_BAD_REQUEST)

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
@api_view(['put'])
@permission_classes([CookieAuthentication])
def PutApplicationActions(request):
    try:
        item = request.data['item']
        action = ApplicationsActions.objects.get(application_id=item['application'], action_id=item['action'])
        action.description = item['description']
        action.save()
    except Exception as e:
        return Response(str(e), status=500)

    return Response("Заявка обновлена", status=200)
    
# Статусы: ["Черновик", "Зарегистрирован", "Проверяется", "Отказано", "Принято", "Удалено"]

def rename_keys(data):
   new_data = {}
   keys = ['ID', 'TypeAction', 'Description', 'ActionID', 'ApplicationID']
   new_keys = ['id', 'type_action', 'description', 'action_id', 'application_id']

   for old_key, new_key in zip(keys, new_keys):
       if old_key in data:
           new_data[new_key] = data[old_key]

   return new_data

@api_view(['put'])
@permission_classes([AllowAny])
def ProcessAnswer(request):
    new_data = request.data
    try:
        if (request.META['HTTP_SECRET_KEY'] != "xg12j4"):
            return HttpResponseForbidden("Access denied")
    except:
        return HttpResponseForbidden("Access denied")
    if 'ID' in new_data.keys():
        new_data = rename_keys(request.data)
    new_data['type_action'] = ''
    app_action = ApplicationsActions.objects.get(id=new_data['id'])
    tmp = ApplicationsActionsSerializer(app_action)
    serializer = ApplicationsActionsSerializer(app_action, data=new_data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response("Заявка не найдена", status=404)

@api_view(['post'])
@permission_classes([AllowAny])
def PlayActions(request, pk):
    actions = ApplicationsActions.objects.filter(application_id=pk)

    actions_data = []
    for action in actions:
        actions_data.append({
            'ID': action.id,
            'TypeAction': action.type_action,
            'Description': action.description,
            'ActionID': action.action_id,
            'ApplicationID': action.application_id,
        })

    headers = {'Content-Type': 'application/json'}

    try:
        print(actions_data)
        response = requests.post('http://localhost:8080/makeanswer', json=actions_data, headers=headers)
        if response.status_code ==   200:
            return JsonResponse({'message': 'Data sent successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Failed to send data'}, status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

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

        response = HttpResponse(user_data['is_moderator'], status=status.HTTP_200_OK)
        print(random_key)
        # max_age=30 * 24 * 60 * 60 
        response.set_cookie("auth", random_key) #,samesite="Lax", secure=False, expires=datetime.utcnow() + timedelta(days=30), path='/',
        return response
    else:
        # Вход не удался
        return HttpResponse({'message': 'Неверные учетные данные логин'}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(method='delete')
@api_view(['post'])
@permission_classes([CookieAuthentication])
def logout_view(request):
    cookie_value = request.COOKIES.get('auth')
    print(cookie_value)
    r.delete(cookie_value)
    response = JsonResponse({'message': 'Успех!'})
    response.delete_cookie('auth')
    return response

class UserViewSet(viewsets.ModelViewSet):
    """Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    model_class = Users
    permission_classes = [AllowAny]

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