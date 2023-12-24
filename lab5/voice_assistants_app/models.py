from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission, UserManager

class Actions(models.Model):
    action_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=255)
    img = models.BinaryField(blank=True, null=True)
    status = models.IntegerField()

    class Meta:
        db_table = 'actions'


class Applications(models.Model):
    application_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    formed_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    customer = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    moderator = models.ForeignKey('Users', models.DO_NOTHING, related_name='applications_moderator_set', blank=True, null=True)

    class Meta:
        db_table = 'applications'


class ApplicationsActions(models.Model):
    application = models.ForeignKey(Applications, models.DO_NOTHING)
    action = models.ForeignKey(Actions, models.DO_NOTHING)
    type_action = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=100)
    

    class Meta:
        db_table = 'applications_actions'
        unique_together = (('application', 'action'),)


class NewUser(UserManager):
    newUser_groups = models.ManyToManyField(Group, related_name='custom_newuser_groups')
    newUser_permissions = models.ManyToManyField(Permission, related_name='custom_newuser_permissions')
    def create_user(self, login, password=None, **extra_fields): 
        user = self.model(login=login, **extra_fields) 
        user.set_password(password)
        user.save(using=self.db)
        return user
    
class Users(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    login = models.CharField(max_length=255, unique=True, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    is_moderator = models.BooleanField(blank=True, null=True)
    fio = models.CharField(db_column='FIO', max_length=255, blank=True, null=True)  # Field name made lowercase.
    groups = models.ManyToManyField(Group, related_name='custom_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions')

    USERNAME_FIELD = 'login'

    objects =  NewUser()
    class Meta:
        db_table = 'users'