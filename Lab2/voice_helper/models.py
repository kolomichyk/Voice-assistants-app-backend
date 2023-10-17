from django.db import models

# Create your models here.

class Actions(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=255)
    img = models.CharField(max_length=80)
    status = models.IntegerField(default=0)

    class Meta:
        db_table = 'actions'
        managed=True

class Applications(models.Model): 
    application_id = models.IntegerField(primary_key=True) 
    status = models.CharField(max_length=20, blank=True, null=True) 
    created_at = models.DateTimeField(blank=True, null=True) 
    formed_at = models.DateTimeField(blank=True, null=True) 
    completed_at = models.DateTimeField(blank=True, null=True) 
    moderator = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True) 
    customer = models.ForeignKey('Users', models.DO_NOTHING, related_name='applications_customer_set', blank=True, null=True) 
 
    class Meta: 
        verbose_name_plural = "Applications" 
        managed=True 
        db_table = 'applications' 
 
 
class ApplicationsActions(models.Model): 
    application = models.OneToOneField(Applications, models.DO_NOTHING, primary_key=True)
    action_id = models.ForeignKey('actions', models.DO_NOTHING) 
    action = models.CharField(max_length=50, null=True) 
    description = models.CharField(max_length=100) 
 
    class Meta: 
        managed=True
        unique_together = (('application', 'action_id'),) 
        db_table = 'applicationsactions' 
 
 
class Users(models.Model): 
    user_id = models.IntegerField(primary_key=True) 
    login = models.CharField(max_length=20, blank=True, null=True) 
    password = models.CharField(max_length=20, blank=True, null=True) 
    is_moderator = models.BooleanField(blank=True, null=True) 
    FIO = models.CharField(max_length=75, blank=True, null=True) 

    class Meta: 
        managed=True 
        db_table = 'users' 
        verbose_name_plural = "Users"


# class YourModel(models.Model):
#     field1 = models.CharField(max_length=50, primary_key=True)
#     field2 = models.IntegerField(primary_key=True)

#     class Meta: 
#         managed=True