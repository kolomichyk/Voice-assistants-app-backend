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
    actions_count = serializers.SerializerMethodField()
    class Meta:
        # Модель, которую мы сериализуем
        model = Applications
        # Поля, которые мы сериализуем
        fields = ["application_id", "status", "created_at", "formed_at", "completed_at", "customer_id", "moderator_id", "actions_count"]

    def get_actions_count(self, obj):
        actions_count = ApplicationsActions.objects.filter(application_id=obj.application_id, description="Какой-то ответ").count()
        return actions_count

class ApplicationsActionsSerializer(serializers.ModelSerializer):
   class Meta:
       model = ApplicationsActions
       fields = ['application', 'action', 'type_action', 'description']

class UsersSerializer(serializers.ModelSerializer):
    is_moderator = serializers.BooleanField(default=False, required=False)
    class Meta:
        # Модель, которую мы сериализуем
        model = Users
        # Поля, которые мы сериализуем
        fields = ["user_id", "login", "password", "is_moderator", "fio"]