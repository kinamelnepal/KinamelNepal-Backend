from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from core.models import BaseModel
from django.utils.text import slugify
from core.managers import BaseModelManager
from django.core.validators import RegexValidator
import uuid
from django.contrib.auth.password_validation import validate_password
class UserManager(BaseUserManager, BaseModelManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if hasattr(extra_fields,'role') and extra_fields.role == 'admin' :
            if not password:
                raise ValueError("Password is required for admin users")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        validate_password(password)  # Uses Django's built-in password validators

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        if not password:
            raise ValueError("Password is required")
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        validate_password(password)  # Uses Django's built-in password validators
        return self.create_user(email, password, **extra_fields)

# User Model
class User(AbstractBaseUser, BaseModel):
    ROLES = [
        ('cleaner', 'Cleaner'),
        ('supervisor', 'Supervisor'),
        ('senior supervisor', 'Senior Supervisor'),
        ('room attendee', 'Room Attendee'),
        ('admin', 'Admin'),
        ('staff','Staff'),
        ('hotel-contact-person','Hotel Contact Person')
    ]
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(
        max_length=255,
        validators=[RegexValidator(r'^[A-Za-z]+$', 'First name must contain only alphabetic characters.')]
    )
    last_name = models.CharField(
        max_length=255,
        validators=[RegexValidator(r'^[A-Za-z]+$', 'First name must contain only alphabetic characters.')]
    )
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128,null=True,blank=True)
    role = models.CharField(max_length=20, choices=ROLES)
    avatar = models.FileField(upload_to="users/avatars/", blank=True, null=True)
    groups = models.ManyToManyField('auth.Group', related_name='users', blank=True) 
    objects = UserManager()
    USERNAME_FIELD = 'email'
    unique_fields = ['email']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """
        Does the user have a specific permission?
        """
        return True

    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label`?
        """
        return True

    def save(self, *args, **kwargs):
        """ Generate slug if not provided """
        if not self.slug:
            self.slug = slugify(self.first_name + "-" + self.last_name)  # More meaningful slug
            # Ensure uniqueness
            while User.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)