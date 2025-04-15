from rest_framework import serializers
from .models import Employee, EmpProfile, EmpEducation


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class EmpProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpProfile
        fields = '__all__'


class EmpEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpEducation
        fields = '__all__'
