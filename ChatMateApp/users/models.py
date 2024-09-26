from django.db import models
import secrets
import uuid
import os
from datetime import *
from django.utils import timezone
from django.contrib.auth.models import AbstractUser,BaseUserManager


# Create your models here.
def user_directory_path(instance, filename):
    unique_filename = f"{uuid.uuid4().hex}{os.path.splitext(filename)[1]}"
    return os.path.join('users', 'uploads', f'user_{instance.id}_{timezone.now().strftime("%Y%m%d%H%M%S")}', unique_filename)

class CustomUserManager(BaseUserManager):
    """
    This is a Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self,email,username,password=None,**extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)
    
class User(AbstractUser):
    first_name = models.CharField(max_length= 75)
    last_name = models.CharField(max_length= 75)
    bio = models.TextField(blank=True, null=True)
    mobile = models.CharField(max_length=11)
    gender = models.CharField(max_length=6, null=False, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Other')
    address = models.CharField(max_length=250)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_image = models.ImageField(upload_to=user_directory_path, null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiration_time = models.DateTimeField(null=True)

    objects = CustomUserManager()
    def __str__(self):
        return f"{self.first_name} - {self.last_name} - {self.bio} - {self.mobile} - {self.gender} - {self.address} - {self.email} - {self.username} - {self.date_of_birth} - {self.profile_image}  - {self.created_at} - {self.updated_at}"
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    @staticmethod
    def generate_reset_token(email, expiration_minutes):
        try:
            user = User.objects.get(email=email)
            otp = str(secrets.randbelow(1000000)).zfill(6)
            user.otp = otp
            user.otp_expiration_time = datetime.now() + timedelta(minutes=expiration_minutes)
            user.save()
            return otp
        except Exception as e:
            print("Otp generation failed:", e)
            return None


