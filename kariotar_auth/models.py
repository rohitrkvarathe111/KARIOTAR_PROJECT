from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser, UserManager
from datetime import timedelta
import time
from django.utils import timezone


class AuditModel(models.Model):
    created_at = models.BigIntegerField()  
    updated_at = models.BigIntegerField()

    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        now = int(timezone.now().timestamp())  
        if not self.pk:
            self.created_at = now
        self.updated_at = now
        super().save(*args, **kwargs)
    

'''  company_type_choise fields
==================================
Private Limited Company (Ltd / LLC)
Sole Proprietorship
Partnership (General & Limited)
Private Limited Company (Ltd / LLC)
Public Limited Company (PLC)
One-Person Company (OPC)
Non-Profit Organization (NPO) / NGO
Cooperative Society
Joint Venture (JV)
Government-Owned Company (Public Sector)
Multinational Corporation (MNC)
'''

class CompanyMaster(AuditModel):

    COMPANY_TYPES = [
        ("Private Limited Company (Ltd / LLC)", "Private Limited Company (Ltd / LLC)"),
        ("Sole Proprietorship", "Sole Proprietorship"),
        ("Partnership (General & Limited)", "Partnership (General & Limited)"),
        ("Public Limited Company (PLC)", "Public Limited Company (PLC)"),
        ("One-Person Company (OPC)", "One-Person Company (OPC)"),
        ("Non-Profit Organization (NPO) / NGO", "Non-Profit Organization (NPO) / NGO"),
        ("Cooperative Society", "Cooperative Society"),
        ("Joint Venture (JV)", "Joint Venture (JV)"),
        ("Government-Owned Company (Public Sector)", "Government-Owned Company (Public Sector)"),
        ("Multinational Corporation (MNC)", "Multinational Corporation (MNC)"),
    ]
    
    company_name = models.CharField(max_length=255)
    sort_name = models.CharField(max_length=100)
    company_type = models.CharField(max_length=100, choices=COMPANY_TYPES)
    GSTIN = models.CharField(max_length=20, unique=True, null=True, blank=True)
    company_email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    company_logo = models.CharField(max_length=250, null=True, blank=True)
    co_token = models.CharField(max_length=255, unique=True, blank=True)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    main_role_id = models.CharField(blank=True, null=True)

    def __str__(self):
        return self.company_name

    class Meta:
        ordering = ["-updated_at"]



class UserType(AuditModel):
    
    is_active = models.BooleanField(default=True)
    user_type = models.CharField(max_length=100, null=False)
    user_id = models.CharField(max_length=100)
    created_by = models.ForeignKey(
        User, related_name="user_type_created", on_delete=models.CASCADE, null=True
    )
    updated_by = models.ForeignKey(
        User, related_name="user_type_updated", on_delete=models.CASCADE, null=True
    )



class UserMaster(AuditModel):
    
    first_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, blank=True, null=True)
    last_name = models.CharField(max_length=200)
    unique_username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=100, unique=True, null=False, blank=False)
    mobile_number = models.CharField(max_length=13, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    company_master = models.ForeignKey(
        CompanyMaster, on_delete=models.CASCADE, null=True
    )
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, null=True, blank=True)
    created_by = models.ForeignKey(
        User, related_name="user_profile_created", on_delete=models.CASCADE, null=True
    )
    updated_by = models.ForeignKey(
        User, related_name="user_profile_updated", on_delete=models.CASCADE, null=True
    )
    assign_role = models.CharField(max_length=250, null=True)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["-updated_at"]
    
class MenuMaster(models.Model):
    subrole_id = models.AutoField(primary_key=True)
    company_master = models.IntegerField()
    sub_role =  models.CharField(max_length=255)
    subrole_url =  models.CharField(max_length=255)
    main_role_id = models.IntegerField()
    main_role = models.CharField(max_length=255)


    class Meta:
        ordering = ["subrole_id"]



