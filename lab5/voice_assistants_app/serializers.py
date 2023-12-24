from voice_assistants_app.models import Actions, Applications, ApplicationsActions, Users
from rest_framework import serializers
from collections import OrderedDict

class ActionsSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Actions
        # Поля, которые мы сериализуем
        fields = ["action_id", "title", "description", "img", "status"]

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            
            return new_fields


class ApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Applications
        # Поля, которые мы сериализуем
        fields = ["application_id", "status", "created_at", "formed_at", "completed_at", "customer_id", "moderator_id"]

class ApplicationsActionsSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = ApplicationsActions
        # Поля, которые мы сериализуем
        fields = ["id", "type_action", "description", "action_id", "application_id"]

class UsersSerializer(serializers.ModelSerializer):
    is_moderator = serializers.BooleanField(default=False, required=False)
    class Meta:
        # Модель, которую мы сериализуем
        model = Users
        # Поля, которые мы сериализуем
        fields = ["user_id", "login", "password", "is_moderator", "fio"]