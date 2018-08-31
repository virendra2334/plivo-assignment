from django.db import models

# Create your models here.


class Account(models.Model):

    is_authenticated = False

    auth_id = models.CharField(default=None, max_length=40)
    username = models.CharField(default=None, max_length=30)

    class Meta:
        db_table = 'account'


    def check_auth_id(self, auth_id):
        if self.auth_id == auth_id:
            self.is_authenticated = True
        
        return self.is_authenticated


class PhoneNumber(models.Model):

    number = models.CharField(default=None, max_length=40)
    account = models.ForeignKey(Account)

    class Meta:
        db_table = 'phone_number'

