from django.db import models


class Actions(models.Model):
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=255)
    img = models.CharField(max_length=80)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'actions'


class Applications(models.Model):
    application_id = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    formed_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    customer = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    moderator = models.ForeignKey('Users', models.DO_NOTHING, related_name='applications_moderator_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'applications'


class Applicationsactions(models.Model):
    application = models.OneToOneField(Applications, models.DO_NOTHING, primary_key=True)
    action = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=100)
    action_id = models.ForeignKey(Actions, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'applicationsactions'
        unique_together = (('application', 'action_id'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class Users(models.Model):
    user_id = models.IntegerField(primary_key=True)
    login = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=20, blank=True, null=True)
    is_moderator = models.BooleanField(blank=True, null=True)
    fio = models.CharField(db_column='FIO', max_length=75, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'users'

# 1 Добавить автополя для PK
# 2 Исправить название таблицы + action_id_id
# 3 MINio