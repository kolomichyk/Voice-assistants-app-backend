from voice_assistants_app.models import Actions, Applications, Applicationsactions, Users
from rest_framework import serializers

class ActionsSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Actions
        # Поля, которые мы сериализуем
        fields = ["id", "title", "description", "img", "status"]


class ApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Applications
        # Поля, которые мы сериализуем
        fields = ["application_id", "status", "created_at", "formed_at", "completed_at", "customer_id", "moderator_id"]

class ApplicationsactionsSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Actions
        # Поля, которые мы сериализуем
        fields = ["application_id", "action", "description", "action_id_id"]

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Actions
        # Поля, которые мы сериализуем
        fields = ["user_id", "login", "password", "is_moderator", "FIO"]