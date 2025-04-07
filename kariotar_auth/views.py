from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from .decorators import verified_user
from rest_framework.permissions import IsAuthenticated
from django.contrib.sessions.backends.db import SessionStore
from django.utils.timezone import localtime, now
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Q
from .models import UserType, UserMaster, CompanyMaster
from .serializers import RegisterUserSerializer, CompanyMasterSerializer, UserMasterSerializer
from django.contrib.auth.models import User
import random
import time
from django.utils import timezone
from helpergenius.views import b2_upload_file, b2_get_signed_url, generate_username
import re

def index(request):
    message = "Oops! The page you are looking for is lost in space."
    error = random.randint(400, 451)
    return render(request, 'index.html', {'message': message, "error": error})


@api_view(['POST'])
def register_company_with_CSA_user(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return Response({"error": "session_id not provided"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        session = SessionStore(session_key=session_id)
        session_data = dict(session.items())
    except Exception:
        return Response({"error": "Invalid session_id"}, status=status.HTTP_400_BAD_REQUEST)
    timestamp = int(time.time())
    K_user_type_id = session_data.get("user_type_id")
    K_user_type = session_data.get('user_type')
    
    if K_user_type_id != "KSA" and K_user_type != "KARIOTAR SUPER ADMIN" :
        return Response({"error": "KARIOTAR SUPER ADMIN not found."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        required_fields = [
            "email", "first_name", "last_name", "company_name", "sort_name", "company_type", 
            "GSTIN", "company_email", "company_mobile", "address", "main_role_id"
        ]
        missing_fields = [field for field in required_fields if field not in request.data or not request.data[field]]

        if missing_fields:
            return Response({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        timestamp = int(time.time())
        user_type = UserType.objects.get(user_type="COMPANY SUPER ADMIN")
        username = generate_username(data.get("first_name"), user_type.user_id)
        company_logo = request.FILES.get("company_logo")
        file_name = re.sub(r"[^\w\.-]", "_", f"{data.get('company_name')}/{username}/{timestamp}")
        # company_logo_path = b2_upload_file(company_logo, file_name)
        company_logo_path = "image.jpg"  # Replace with actual upload logic if needed
        
        auth_master = {
            "email": data.get("email"),
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "username": username,
            "password": username,
        }
        
        company_master = {
            "company_name": data.get("company_name"),
            "sort_name": data.get("sort_name"),
            "company_type": data.get("company_type"),
            "GSTIN": data.get("GSTIN"),
            "company_email": data.get("company_email"),
            "mobile": data.get("company_mobile"),
            "company_logo": company_logo_path,
            "address": data.get("address"),
            "main_role_id": data.get("main_role_id"),
        }
        
        user_master = {
            "first_name": data.get("first_name"),
            "middle_name": data.get("middle_name"),
            "last_name": data.get("last_name"),
            "unique_username": username,
            "email": data.get("email"),
            "mobile_number": data.get("company_mobile"),
            "is_admin": True,
            "address": data.get("address"),
        }
        
        with transaction.atomic():
            auth_object = RegisterUserSerializer(data=auth_master)
            company_object = CompanyMasterSerializer(data=company_master)
            
            if not auth_object.is_valid():
                return Response({"auth_errors": auth_object.errors}, status=status.HTTP_400_BAD_REQUEST)
            if not company_object.is_valid():
                return Response({"company_errors": company_object.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            auth_instance = auth_object.save()
            company_instance = company_object.save()
            
            user_master.update({
                "auth_user": auth_instance.id,
                "company_master": company_instance.id,
                "user_type": user_type.id,
                "created_by": auth_instance.id,
                "updated_by": auth_instance.id,
                "created_at": timestamp,
                "updated_at": timestamp,
            })
            
            usermaster_object = UserMasterSerializer(data=user_master)
            if not usermaster_object.is_valid():
                return Response({"user_errors": usermaster_object.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            usermaster_object.save()
            return Response({"message": "Company registered successfully"}, status=status.HTTP_201_CREATED)
    
    except UserType.DoesNotExist:
        return Response({"error": "User type not found"}, status=status.HTTP_400_BAD_REQUEST)
    except KeyError as e:
        return Response({"error": f"Missing required field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"Internal Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['POST'])
def User_login(request):
    try:
        required_fields = ["email", "password"]
        missing_fields = [field for field in required_fields if field not in request.data or not request.data[field]]
        
        if missing_fields:
            return Response({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = authenticate(request, username=user.username, password=password)
        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        # login(request, user)                            # TODO: change and comment this line to
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        
        request.session.create()
        session_id = request.session.session_key
        request.session["login_time"]= localtime(user.last_login).isoformat()
        request.session["user_id"] = user.id
        request.session["username"] = user.username
        request.session["email"] = user.email
        request.session["first_name"] = user.first_name
        request.session["last_name"] = user.last_name
        try:           
            user_object =  UserMaster.objects.get(email=email)
            request.session["user_master_id"] = user_object.id
            request.session["unique_username"] = user_object.unique_username
            request.session["mobile_number"] = user_object.mobile_number
            request.session["is_admin"] = user_object.is_admin
            request.session["user_type"] = user_object.user_type.user_type
            request.session["user_type_id"] = user_object.user_type.user_id

            company_object = CompanyMaster.objects.get(id=user_object.company_master.id)
            request.session["company_id"] = company_object.id
            request.session["company_name"] = company_object.company_name
            request.session["sort_name"] = company_object.sort_name
            request.session["company_type"] = company_object.company_type
            request.session["company_email"] = company_object.company_email
            request.session.save()
            # request.session.set_expiry(120) 
        except Exception as e:
            return Response({"message": f"Login Field check login credetial or contact with administration {str(e)}",})

        return Response({
            "message": "Login successful",
            "login_time": localtime(user.last_login).isoformat(),
            "session_id": session_id,
            "session_data": dict(request.session.items())
            }, status=status.HTTP_200_OK)
    
    except KeyError as e:
        return Response({"error": f"Missing required field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"Internal Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
def User_logout(request):
    session_id = request.GET.get('session_id')
    all_logout = request.GET.get('all_logout', 'false').lower() == 'true'
    if session_id:
        try:
            session = Session.objects.get(pk=session_id)
            session_data = session.get_decoded()
            user_id = session_data.get("user_id")
            # session.delete()
        except Session.DoesNotExist:
            return Response({"error": "Session ID not found"}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"error": "Session ID not provided"}, status=status.HTTP_401_UNAUTHORIZED)
    
    if all_logout and user_id:
        # Delete all sessions where the same user_id exists
        all_sessions = Session.objects.filter(expire_date__gt=now())
        for s in all_sessions:
            s_data = s.get_decoded()
            if s_data.get("user_id") == user_id:
                s.delete()
    else:
        # Delete only the provided session
        session.delete()

    request.session.flush() 
    user = request.session.get("user")
    request.session.flush()
    
    return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)




@api_view(['GET'])
def User_data(request):
    session_id = request.GET.get("session_id")
    if session_id:
        request.session = SessionStore(session_key=session_id)
    else:
        return Response({"error": "session_id not provided"}, status=400)
    
    session_id = dict(request.session.items())
    return Response(session_id)


@api_view(['POST'])
def create_user_for_company(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return Response({"error": "session_id not provided"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        session = SessionStore(session_key=session_id)
        session_data = dict(session.items())
    except Exception:
        return Response({"error": "Invalid session_id"}, status=status.HTTP_400_BAD_REQUEST)
    timestamp = int(time.time())
    K_user_type_id = session_data.get("user_type_id")
    K_user_type = session_data.get('user_type')
    K_user_id = session_data.get('user_id')
    
    if K_user_type_id != "KSA" and K_user_type != "KARIOTAR SUPER ADMIN" :
        return Response({"error": "KARIOTAR SUPER ADMIN not found."}, status=status.HTTP_400_BAD_REQUEST)

    required_fields = ["company_id","email", "first_name", "last_name", "address", "mobile_number", "user_type"]
    missing_fields = [field for field in required_fields if field not in request.data or not request.data[field]]
    if missing_fields:
            return Response({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)
    
    data = request.data
    required_fields = {"company_id", "email", "first_name", "last_name", "address", "mobile_number", "user_type"}
    missing_fields = required_fields - data.keys()
    
    if missing_fields:
        return Response({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        company_obj = CompanyMaster.objects.get(id=data["company_id"])
        user_type = UserType.objects.get(id=data["user_type"])
    except CompanyMaster.DoesNotExist:
        return Response({"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND)
    except UserType.DoesNotExist:
        return Response({"error": "User type not found."}, status=status.HTTP_404_NOT_FOUND)
    
    username = generate_username(data["first_name"], user_type.user_id)  
    auth_master = {
        "email": data["email"],
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "username": username,
        "password": username,
    }
    user_master = {
        "first_name": data["first_name"],
        "middle_name": data["middle_name"],
        "last_name": data["last_name"],
        "unique_username": username,
        "email": data["email"],
        "mobile_number": data["mobile_number"],
        "is_admin": False,
        "address": data["address"],
        "auth_user": None,  # To be set later
        "company_master": company_obj.id,
        "user_type": user_type.id,
        "created_by": K_user_id,
        "updated_by": K_user_id,
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    try:
        with transaction.atomic():
            auth_serializer = RegisterUserSerializer(data=auth_master)
            if not auth_serializer.is_valid():
                return Response({"auth_errors": auth_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            auth_instance = auth_serializer.save()
            
            user_master["auth_user"] = auth_instance.id
            user_serializer = UserMasterSerializer(data=user_master)
            if not user_serializer.is_valid():
                return Response({"user_errors": user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            user_serializer.save()
            
            return Response({
                "message": f"{data['first_name']} has been successfully registered with the login email {data['email']} and associated with the {company_obj.company_name} company.",
                # "first_name": data["first_name"],
                "username": username
            }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": f"Internal Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@verified_user("KSA", "KARIOTAR SUPER ADMIN")
def Chnage_user_password(request):

    new_password = request.data.get('new_password')
    username = request.data.get('username')

    if not username or not new_password:
        return Response({"error": "username and new_password are required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user_master = UserMaster.objects.get(Q(unique_username=username) | Q(email=username))
        user_object = User.objects.get(username=user_master.unique_username)
        user_object.set_password(new_password)
        user_object.save()
        all_sessions = Session.objects.filter(expire_date__gt=now())
        for s in all_sessions:
            s_data = s.get_decoded()
            if s_data.get("user_id") == user_object.id:
                s.delete()

        return Response({
            "message": f"Password for user {user_object.username} has been changed successfully, {user_object.first_name}.",
            "Email": f"The set password has been shared with the email {user_master.email}."
            }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Internal Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@verified_user("KSA", "KARIOTAR SUPER ADMIN")
def user_comapny_helper(request, type):
    
    if type == "user":
        return Response({
            "company_list": list(CompanyMaster.objects.filter(is_active=True).values("id", "company_name", "company_email")),
            "user_type_list": list(UserType.objects.filter(is_active=True).values("id", "user_type", "user_id"))
        }, status=status.HTTP_200_OK)

    if type == "company":
        return Response({
            "company_types": [{"code": name, "company_type": name} for name, _ in CompanyMaster.COMPANY_TYPES]
        }, status=status.HTTP_200_OK)

    return Response({"error": "Invalid type provided. Please provide 'user' or 'company' only."}, status=status.HTTP_400_BAD_REQUEST)

