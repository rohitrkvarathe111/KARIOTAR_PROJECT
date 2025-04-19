from rest_framework import serializers
from .models import Employee, EmpProfile, EmpEducation, EmpAttendance
from datetime import datetime


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        # fields = '__all__'
        exclude = ["id", "created_at", "updated_at", "is_active", "company_master", 
                    "user_master", "user", "created_by", "updated_by"]


class EmpProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpProfile
        # fields = '__all__'
        exclude = ["id", "employee", "user", "user_master", "company_master", 
                   "created_at", "updated_at", "verified_status", "is_active"]


class EmpEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpEducation
        # fields = '__all__'
        exclude = ["id", "employee", "user", "user_master", "company_master", 
                   "created_at", "updated_at", "verified_status", "is_active"]


class EmpAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpAttendance
        # fields = '__all__'
        exclude = ["id", "employee", "company_master", 
                   "created_at", "updated_at",]