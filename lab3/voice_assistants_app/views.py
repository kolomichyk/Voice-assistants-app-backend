from django.shortcuts import render
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from voice_assistants_app.serializers import ActionsSerializer, ApplicationsSerializer, ApplicationsactionsSerializer
from voice_assistants_app.models import Actions, Applications, Users, Applicationsactions
from rest_framework.decorators import api_view
import json
from datetime import datetime

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
    return Response(serializer.data)

@api_view(['Post'])
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

@api_view(['Get'])
def get_detail(request, pk, format=None):
    action = get_object_or_404(Actions, pk=pk)
    if request.method == 'GET':
        """
        Возвращает информацию об услуге
        """
        serializer = ActionsSerializer(action)
        return Response(serializer.data)

@api_view(['Put'])
def put_detail(request, pk, format=None):
    """
    Обновляет информацию об акции
    """
    action = get_object_or_404(Actions, pk=pk)
    serializer = ActionsSerializer(action, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Delete'])
def delete_detail(request, pk, format=None):    
    """
    Удаляет информацию об услуге
    """
    action = get_object_or_404(Actions, pk=pk)
    action.delete()
    actions = Actions.objects.all()
    serializer = ActionsSerializer(actions, many=True)
    return Response(serializer.data)


@api_view(['Put'])
def put_detail(request, pk, format=None):
    """
    Добавление заявки в услугу
    """
    action = get_object_or_404(Actions, pk=pk)
    serializer = ActionsSerializer(action, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Put'])
def put_detail_to_application(request, pk, format=None):
    """
    Добавление заявки в услугу
    """
    current_user = CurrentUserSingleton.get_instance()
    try: 
        Applications.objects.filter(customer_id=current_user.user_id, status="Зарегистрирован").latest('creation_date')
    except:
        application = Applications(
            application_id = 5,
            status = "зарегистрирован",
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            formed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            customer_id = 1,
            moderator_id = 1
        )
        application.save()
    action = Actions.objects.get(id=pk)
    try:
        applicationsactions = Applicationsactions.objects.get(application_id=application.application_id, action_id_id=action.id)
        return Response("Такое действие уже добавлено заявку")
    except Applicationsactions.DoesNotExist:
        applicationsactions = Applicationsactions(
            application_id = application.application_id,
            action_id_id = action.id
        )
        applicationsactions.save()
    applications = Applications.objects.all()
    serializer = ApplicationsSerializer(applications, many=True)
    return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Get'])
def get_list_applications(request, format=None):
    """
    Возвращает список заявок
    """
    print('get')
    applications = Applications.objects.all()
    serializer = ApplicationsSerializer(applications, many=True)
    current_user = CurrentUserSingleton.get_instance()
    # print(current_user.password)
    return Response(serializer.data)

@api_view(['Get'])
def get_detail_applications(request, pk, format=None):
    applications = get_object_or_404(Applications, pk=pk)
    if request.method == 'GET':
        """
        Возвращает информацию о заявке
        """
        serializer = ApplicationsSerializer(applications)
        return Response(serializer.data)
    
@api_view(['Put'])
def put_detail_applications(request, pk, format=None):
    """
    Обновляет информацию о заявке
    """
    applications = get_object_or_404(Applications, pk=pk)
    serializer = ApplicationsSerializer(applications, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Delete'])
def delete_detail_application(request, pk, format=None):    
    """
    Удаляет информацию о заявке
    """
    applications = get_object_or_404(Applications, pk=pk)
    applications.delete()
    applications = Applications.objects.all()
    serializer = ApplicationsSerializer(applications, many=True)
    return Response(serializer.data)

@api_view(['Put'])
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
    
@api_view(['Put'])
def put_detail_applications_user(request, pk, format=None):
    """
    Обновляет информацию о заявке
    """
    applications = get_object_or_404(Applications, pk=pk)
    serializer = ApplicationsSerializer(applications, data=request.data)
    # print(applications.application_id)
    if (applications.status == "зарегистрирован" and request.data['status'] == "проверяется"):
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response("Неверный статус заявки", status=status.HTTP_400_BAD_REQUEST)

# Статусы: ["Зарегистрирован", "Проверяется", "Отказано", "Принято", "Удалено"]