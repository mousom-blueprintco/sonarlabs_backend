from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.hashers import make_password

class UserManager(BaseUserManager):
     
    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        first_name = extra_fields.pop('first_name', None)
        last_name = extra_fields.pop('last_name', None)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    first_name =  models.CharField(max_length=255,blank=False, null=False)
    last_name =  models.CharField(max_length=255, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    password = models.CharField( blank=False, null=False,max_length=255)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verify_token = models.CharField(max_length=255, null=True)
    otp_details = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'password']

    def __str__(self):
        return self.email

class Project(models.Model):
    project_id = models.CharField(max_length=255,blank=True, null=True)
    project_name = models.CharField(max_length=255,blank=True, null=True)
    created_by = models.EmailField(blank=True, null=True)
    total_files_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)
    
    def __str__(self):
        return self.project_id
       
class File(models.Model):
    file_id = models.CharField(max_length=255,blank=True, null=True)
    file_name = models.CharField(max_length=255,blank=True, null=True)
    file_type = models.CharField(max_length=255,blank=True, null=True)
    dir = models.CharField(max_length=255,blank=True, null=True)
    s3_url = models.TextField(blank=True, null=True,max_length=500)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files', null=True)
    uploaded_on = models.DateTimeField(auto_now_add=True,null=True)
    uploaded_by = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)
    
    def __str__(self):
        return self.file_id
    

