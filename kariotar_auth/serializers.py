from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Q
from .models import CompanyMaster, UserMaster
import re
import uuid


class RegisterUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password','first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        """Validate email and username uniqueness."""
        if User.objects.filter(Q(username=data['username']) | Q(email=data['email'])).exists():
            raise serializers.ValidationError({"email": "Email is already in use"})
    
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user



class CompanyMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyMaster
        fields = ['company_name', 'sort_name', 'company_type', 'GSTIN', 'company_email', 'mobile', 'company_logo', 'address', 'main_role_id']
        read_only_fields = ['co_token']  

    # def validate_GSTIN(self, value):
    #     """Validate GSTIN format (assuming Indian GST format)."""
    #     if value:
    #         gstin_regex = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$'
    #         if not re.match(gstin_regex, value):
    #             raise serializers.ValidationError("Invalid GSTIN format.")
    #     return value

    def validate_mobile(self, value):
        """Validate mobile number format."""
        if not re.match(r'^[6-9]\d{9}$', value):
            raise serializers.ValidationError("Invalid mobile number format.")
        return value

    def validate(self, data):
        """Custom validation for unique fields in one query."""
        company_email = data.get('company_email')
        gstin = data.get('GSTIN')
        
        filters = {}
        if company_email:
            filters['company_email'] = company_email
        if gstin:
            filters['GSTIN'] = gstin
        
        if filters and CompanyMaster.objects.filter(**filters).exists():
            errors = {}
            if 'company_email' in filters:
                errors['company_email'] = "A company with this email already exists."
            if 'GSTIN' in filters:
                errors['GSTIN'] = "A company with this GSTIN already exists."
            raise serializers.ValidationError(errors)
        
        return data

    def create(self, validated_data):
        if 'co_token' not in validated_data or not validated_data['co_token']:
            validated_data['co_token'] = str(uuid.uuid4())  
        return super().create(validated_data)
    

class UserMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMaster
        fields = '__all__'
    
    def validate(self, data):
        unique_username = data.get("unique_username")
        email = data.get("email")
        mobile_number = data.get("mobile_number")
        
        existing_user = UserMaster.objects.filter(
            Q(unique_username=unique_username) | 
            Q(email=email) | 
            Q(mobile_number=mobile_number)
        ).first()
        
        if existing_user:
            errors = {}
            if existing_user.unique_username == unique_username:
                errors["unique_username"] = "This username is already taken."
            if existing_user.email == email:
                errors["email"] = "This email is already registered."
            if mobile_number and existing_user.mobile_number == mobile_number:
                errors["mobile_number"] = "This mobile number is already registered."
            
            if errors:
                raise serializers.ValidationError(errors)
        
        return data


    def create(self, validated_data):
        return UserMaster.objects.create(**validated_data)