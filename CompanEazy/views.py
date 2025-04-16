from django.shortcuts import render
import random
from django.utils.timezone import now
from kariotar_auth.decorators import verified_user
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.contrib.sessions.backends.db import SessionStore
from kariotar_auth.models import CompanyMaster, UserMaster, UserType
from kariotar_auth.serializers import RegisterUserSerializer, UserMasterSerializer
from .serializers import EmployeeSerializer, EmpProfileSerializer, EmpEducationSerializer, EmpAttendanceSerializer
from . models import Employee, EmpProfile, EmpEducation, EmpAttendance
from helpergenius.views import generate_username, b2_upload_file
from django.db import transaction
import time
import re

def index(request):
    message = "Oops! The page you are looking for is lost in space."
    error = random.randint(400, 451)
    return render(request, 'index.html', {'message': message, "error": error})

@api_view(['POST'])
@verified_user("CHRA", "COMPANY HR ADMIN")
def register_company_employee(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return Response({"error": "session_id not provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        session = SessionStore(session_key=session_id)
        session_data = dict(session.items())
        company_id = session_data.get("company_id")
        created_by = session_data.get("user_id")
    except Exception:
        return Response({"error": "Invalid session_id"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not company_id:
        return Response({"error": "Company ID missing in session"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        company_object = CompanyMaster.objects.get(id=company_id, is_active=True)
    except CompanyMaster.DoesNotExist:
        return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

    timestamp = int(time.time())
    data = request.data
    required_fields = {"email", "first_name", "middle_name", "last_name", "user_type", "mobile_number", 
                       "address", "assets", "emp_code", "date_joined", "admin_manager_id", "funt_manager_id", 
                       "position", "department", "emp_type", "group", "salary_lpa"}
    missing_fields = required_fields - data.keys()
    if missing_fields:
        return Response({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)
    
    file_fields = {"offer_letter", "emp_agreement", "nda"}
    media_upload = {field: request.FILES.get(field) for field in file_fields}
    
    try:
        user_type = UserType.objects.get(id=data["user_type"])
    except UserType.DoesNotExist:
        return Response({"error": "Invalid user_type"}, status=status.HTTP_400_BAD_REQUEST)
    
    username = generate_username(data["first_name"], user_type.type_code)
    
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
        "company_master": company_object.id,
        "user_type": user_type.id,
        "created_by": created_by,
        "updated_by": created_by,
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    
    uploaded_files = {}
    for field, file in media_upload.items():
        file_name = re.sub(r"[^\w\.-]", "_", f"{data['first_name']}/{field}/{username}/{int(time.time())}")
        # uploaded_files[field] = b2_upload_file(file, file_name)
        uploaded_files[field] = file_name  # Change this when integrating file storage
    
    try:
        with transaction.atomic():
            auth_serializer = RegisterUserSerializer(data=auth_master)
            if auth_serializer.is_valid():
                auth_instance = auth_serializer.save()
                user_master["auth_user"] = auth_instance.id
            else:
                return Response({"auth_errors": auth_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            user_serializer = UserMasterSerializer(data=user_master)
            if user_serializer.is_valid():
                usermaster_instance = user_serializer.save()
            else:
                # Rollback: Delete auth_instance if user creation fails
                auth_instance.delete()
                return Response({"user_errors": user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                emp_object = Employee.objects.create(
                    emp_name=f"{data['first_name']} {data['middle_name']} {data['last_name']}",
                    emp_code=data["emp_code"],
                    company_master=company_object,
                    user_master=usermaster_instance,
                    user=auth_instance,
                    group=data["group"],
                    emp_type=data["emp_type"],
                    department=data["department"],
                    position=data["position"],
                    funt_manager_id=data["funt_manager_id"],
                    admin_manager_id=data["admin_manager_id"],
                    date_joined=data["date_joined"],
                    salary_lpa=data["salary_lpa"],
                    is_active=True,
                    offer_letter=uploaded_files.get("offer_letter"),
                    emp_agreement=uploaded_files.get("emp_agreement"),
                    nda=uploaded_files.get("nda"),
                    assets=data["assets"],
                    created_by_id=created_by,
                    updated_by_id=created_by,
                )
                emp_profile = EmpProfile.objects.create(
                    emp_name=emp_object.emp_name,
                    emp_code=emp_object.emp_code,
                    employee=emp_object,
                    user=auth_instance,
                    company_master=company_object,
                    user_master=usermaster_instance,
                )
                emp_profile = EmpEducation.objects.create(
                    emp_name=emp_object.emp_name,
                    emp_code=emp_object.emp_code,
                    employee=emp_object,
                    user=auth_instance,
                    company_master=company_object,
                    user_master=usermaster_instance,
                )
            except Exception as e:
                # Rollback: Delete both user_master and auth_instance if employee creation fails
                transaction.on_commit(lambda: usermaster_instance.delete())
                transaction.on_commit(lambda: auth_instance.delete())
                return Response({"employee_errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({"message": f"{emp_object.emp_name} as Employee registered successfully 😊"}, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@verified_user("CHRA", "COMPANY HR ADMIN")
def get_registered_employee(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return Response({"error": "session_id not provided"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        session = SessionStore(session_key=session_id)
        session_data = dict(session.items())
        company_id = session_data.get("company_id")
    except Exception:
        return Response({"error": "Invalid session_id"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not company_id:
        return Response({"error": "Company ID missing in session"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        company_object = CompanyMaster.objects.get(id=company_id, is_active=True)
    except CompanyMaster.DoesNotExist:
        return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
    
    page = int(request.GET.get('page', 1))
    length = int(request.GET.get('length', 10))
    query_params = {
        "company_master": company_object,  
        "is_active": True
    }

    emp_name = request.GET.get('emp_name')
    if emp_name:
        query_params["emp_name__icontains"] = emp_name

    emp_code = request.GET.get('emp_code')
    if emp_code:
        query_params["emp_code__icontains"] = emp_code

    filter_count = Employee.objects.filter(**query_params).count()
    employee_data = Employee.objects.filter(**query_params).values()[(page-1)*length:page*length]
    
    return Response({
        "page": page,
        "filter_count": filter_count,
        "table": employee_data
    }, status=status.HTTP_200_OK)




@api_view(['GET','PUT'])
@verified_user("CHRA", "COMPANY HR ADMIN")
def update_emp_details(request, emp_id):
    
    try:
        employee = Employee.objects.get(id=emp_id) 
    except Employee.DoesNotExist:
        return Response({"error": "Employee data not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response(EmployeeSerializer(employee).data, status=status.HTTP_200_OK)

    data = request.data.copy()

    # TODO : Update the employee details here
    # "emp_name", "emp_code", "group", "emp_type", "department", "position", "salary_lpa", "date_joined", 
    # "office_mobile", "office_email", "offer_letter", "emp_agreement", "nda", "resignation", "assets", "funt_manager", "admin_manager",
    
    file_fields = {"offer_letter", "emp_agreement", "nda", "resignation"}
    media_upload = {field: request.FILES.get(field) for field in file_fields}

    uploaded_files = {}
    for field, file in media_upload.items():
        file_name = getattr(employee, field, None)
        # uploaded_files[field] = b2_upload_file(file, file_name)
        if file_name is None:
            file_name = re.sub(r"[^\w\.-]", "_", f"{employee.user_master.first_name}/{field}/{employee.user_master.unique_username}/{int(time.time())}")
        uploaded_files[field] = file_name  # Change this when integrating file storage
    data.update(uploaded_files)

    emp_serializer = EmployeeSerializer(employee, data, partial=True)
    if emp_serializer.is_valid():
        emp_serializer.save()
        return Response(
            emp_serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(emp_serializer.errors,
                         status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET','PUT'])
@verified_user("CHRA", "COMPANY HR ADMIN")
def update_emp_profile(request, emp_id):
    
    try:
        emp_profile = EmpProfile.objects.get(employee_id=emp_id) 
    except EmpProfile.DoesNotExist:
        return Response({"error": "Employee data not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response(EmpProfileSerializer(emp_profile).data, status=status.HTTP_200_OK)

    data = request.data.copy()

    # TODO : Update the employee details here data
    # "emp_name", "emp_code", "personal_mobile", "personal_email", "dob", "blood_group", "gender", "pan", "aadhar", "bank_name", "bank_acc_no", "bank_ifsc", "pf_acc", "uan_acc"
    # "insurance_meta_data", "emergency_mobile", "emergency_contact_name", "emergency_contact_relation", "current_address", "current_city", "current_state", "current_pincode", 
    # "permanent_address", "permanent_city", "permanent_state", "permanent_pincode", "marital_status", "profile_links"
    
    file_fields = {"pan_img", "aadhar_img", "emp_img", "bank_img", }
    media_upload = {field: request.FILES.get(field) for field in file_fields}

    uploaded_files = {}
    for field, file in media_upload.items():
        file_name = getattr(emp_profile, field, None)
        # uploaded_files[field] = b2_upload_file(file, file_name)
        if file_name is None:
            file_name = re.sub(r"[^\w\.-]", "_", f"{emp_profile.user_master.first_name}/{field}/{emp_profile.user_master.unique_username}/{int(time.time())}")
        uploaded_files[field] = file_name  # Change this when integrating file storage
    data.update(uploaded_files)

    emp_serializer = EmpProfileSerializer(emp_profile, data, partial=True)
    if emp_serializer.is_valid():
        emp_serializer.save()
        return Response(
            emp_serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(
            emp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET','PUT'])
@verified_user("CHRA", "COMPANY HR ADMIN")
def update_emp_education(request, emp_id):
    
    try:
        emp_profile = EmpEducation.objects.get(employee_id=emp_id) 
    except EmpEducation.DoesNotExist:
        return Response({"error": "Employee data not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response(EmpEducationSerializer(emp_profile).data, status=status.HTTP_200_OK)

    data = request.data.copy()

    # TODO : Update the employee details here data
    # "emp_name", "emp_code", "personal_mobile", "personal_email", "dob", "blood_group", "gender", "pan", "aadhar", "bank_name", "bank_acc_no", "bank_ifsc", "pf_acc", "uan_acc"
    # "insurance_meta_data", "emergency_mobile", "emergency_contact_name", "emergency_contact_relation", "current_address", "current_city", "current_state", "current_pincode", 
    # "permanent_address", "permanent_city", "permanent_state", "permanent_pincode", "marital_status", "profile_links"
    
    file_fields = {"ssc_img", "hsc_img", "ug_img", "pg_img", "other1_img", "other2_img"}
    media_upload = {field: request.FILES.get(field) for field in file_fields}

    uploaded_files = {}
    for field, file in media_upload.items():
        file_name = getattr(emp_profile, field, None)
        # uploaded_files[field] = b2_upload_file(file, file_name)
        if file_name is None:
            file_name = re.sub(r"[^\w\.-]", "_", f"{emp_profile.user_master.first_name}/{field}/{emp_profile.user_master.unique_username}/{int(time.time())}")
        uploaded_files[field] = file_name  # Change this when integrating file storage
    data.update(uploaded_files)

    emp_serializer = EmpEducationSerializer(emp_profile, data, partial=True)
    if emp_serializer.is_valid():
        emp_serializer.save()
        return Response(
            emp_serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(
            emp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','POST'])
@verified_user("CHRA", "COMPANY HR ADMIN")
def verified_emp(request, emp_id):
    try:
        employee = Employee.objects.get(id=emp_id) 
        emp_profile = EmpProfile.objects.get(employee_id=emp_id)
        emp_edu = EmpEducation.objects.get(employee_id=emp_id) 
    except (Employee.DoesNotExist, EmpProfile.DoesNotExist, EmpEducation.DoesNotExist):
        return Response({"error": "Employee data not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        verified_pro = request.data.get('verified_pro',[])
        verified_edu = request.data.get('verified_edu',[])
        if not isinstance(verified_pro, list) or not isinstance(verified_edu, list):
            return Response({"error": "Only list type allowed"}, status=400)

        emp_profile.verified_status = verified_pro
        emp_edu.verified_status = verified_edu
        
        emp_profile.save()
        emp_edu.save()
        return Response({"verified": employee.emp_name, "emp_profile_verified": emp_profile.verified_status, 
                        "emp_edu_verified": emp_edu.verified_status}, status=status.HTTP_200_OK)
    
    emp = EmployeeSerializer(employee).data
    emp_edu = EmpEducationSerializer(emp_profile).data
    emp_profile = EmpProfileSerializer(emp_profile).data
    return Response({
        "employee": emp, 
        "emp_profile": emp_profile, 
        "emp_education": emp_edu
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
def mark_attendance(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return Response({"error": "session_id not provided"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        session = SessionStore(session_key=session_id)
        session_data = dict(session.items())
    except Exception:
        return Response({"error": "Invalid session_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        employee = Employee.objects.get(user_master_id=session_data.get('user_master_id'))
    except Employee.DoesNotExist:
        return Response({"error": "Employee data not found"}, status=status.HTTP_404_NOT_FOUND)
    attendance_choices_set = set(choice[0] for choice in EmpAttendance.ATTENDANCE_STATUS_CHOICES)
    attendance_choices = [{"code": name, "company_type": name} for name in attendance_choices_set]

    attendance_status = request.data.get('status')
    if attendance_status not in attendance_choices_set:
        return Response({"error": "Invalid attendance status"}, status=status.HTTP_400_BAD_REQUEST)
    
    check_in = request.data.get('check_in')
    check_in_ip = request.data.get('check_in_ip')
    check_in_img = request.FILES.get('check_in_img')
    check_in_cords = request.data.get('check_in_cords')
    check_in_remark = request.data.get('check_in_remark')


    

    return Response({
        "message": "Attendance marked successfully",
        "data": attendance_choices,
    }, status=status.HTTP_200_OK)
