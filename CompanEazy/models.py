from django.db import models
from kariotar_auth.models import User, CompanyMaster, UserMaster
from datetime import datetime
# from django.contrib.auth import get_user_model


class AuditModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # Set only once at creation
    updated_at = models.DateTimeField(auto_now=True)  # Updates every time save() is called
    class Meta:
        abstract = True


class Employee(AuditModel):
    EMPLOYEE_TYPES = [
        ('Full-Time', 'Full-Time'),
        ('Part-Time', 'Part-Time'),
        ('Contract', 'Contract'),
        ('Intern', 'Intern'),
        ('Freelancer', 'Freelancer'),
        ('Temporary', 'Temporary'),
        ('Consultant', 'Consultant'),
        ('Apprentice', 'Apprentice'),
        ('Volunteer', 'Volunteer'),
        ('Seasonal', 'Seasonal'),
        ('Probationary', 'Probationary'),
        ('Remote', 'Remote'),
        ]

    emp_name = models.CharField(max_length=255)  # full name of user_master
    emp_code = models.CharField(max_length=255)
    company_master = models.ForeignKey(CompanyMaster, on_delete=models.CASCADE)
    user_master = models.ForeignKey(UserMaster, on_delete=models.CASCADE, related_name="employees")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="employee_records")
    group = models.CharField(max_length=255)
    emp_type = models.CharField(max_length=20, choices=EMPLOYEE_TYPES)
    department = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    funt_manager = models.ForeignKey(UserMaster, on_delete=models.CASCADE, related_name="functional_employees")
    admin_manager = models.ForeignKey(UserMaster, on_delete=models.CASCADE, related_name="admin_employees")
    salary_lpa = models.BigIntegerField(default=0)  # salary in paisa format
    date_joined = models.DateField()
    office_mobile = models.CharField(max_length=15, blank=True, null=True)
    office_email = models.EmailField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    offer_letter = models.CharField(max_length=255, blank=True, null=True)
    emp_agreement = models.CharField(max_length=255, blank=True, null=True)
    nda = models.CharField(max_length=255, blank=True, null=True)
    resignation = models.CharField(max_length=255, blank=True, null=True)
    resignation_dt = models.DateField(blank=True, null=True)
    assets = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="employees_created"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="employees_updated"
    )


    def __str__(self):
        return self.emp_name
    


class EmpProfile(AuditModel):

    MARITAL_STATUS_CHOICES = [
            ("Single", "Single"),
            ("Married", "Married"),
            ("Divorced", "Divorced"),
            ("Widowed", "Widowed"),
            ("Separated", "Separated"),
            ("Engaged", "Engaged"),
            ("In a Relationship", "In a Relationship"),
            ("Complicated", "Complicated"),
        ]
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Transgender", "Transgender"),
        ("Non-Binary", "Non-Binary"),
        ("Genderfluid", "Genderfluid"),
        ("Agender", "Agender"),
        ("Two-Spirit", "Two-Spirit"),
        ("Other", "Other"),
        ("Prefer not to say", "Prefer not to say"),
    ]
    emp_name = models.CharField(max_length=255)
    emp_code = models.CharField(max_length=50, unique=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="employee_id")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auth_id")
    user_master = models.ForeignKey(UserMaster, on_delete=models.CASCADE, related_name="user_master_id")
    company_master = models.ForeignKey(CompanyMaster, on_delete=models.CASCADE)
    personal_mobile = models.CharField(max_length=15, null=True, blank=True)
    personal_email = models.EmailField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=10, null=True, blank=True)
    gender = models.CharField(max_length=30, choices=GENDER_CHOICES)
    pan = models.CharField(max_length=20, null=True, blank=True)
    pan_img = models.CharField(max_length=255, null=True, blank=True)
    aadhar = models.CharField(max_length=20, null=True, blank=True)
    aadhar_img = models.CharField(max_length=255, null=True, blank=True)
    emp_img = models.CharField(max_length=255, null=True, blank=True)
    bank_name = models.CharField(max_length=255)
    bank_acc_no = models.CharField(max_length=80, null=True, blank=True)
    bank_ifsc = models.CharField(max_length=30)
    bank_img = models.CharField(max_length=255, null=True, blank=True)
    pf_acc = models.CharField(max_length=50, null=True, blank=True)
    uan_acc = models.CharField(max_length=50, null=True, blank=True)
    insurance_meta_data = models.JSONField(null=True, blank=True)
    verified_status = models.CharField(max_length=20, blank=True, null=True)
    emergency_mobile = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact_relation = models.CharField(max_length=150, blank=True, null=True)
    current_address = models.TextField(null=True, blank=True)
    current_city = models.CharField(max_length=100, null=True, blank=True)
    current_state = models.CharField(max_length=100, null=True, blank=True)
    current_pincode = models.CharField(max_length=10, null=True, blank=True)
    permanent_address = models.TextField(null=True, blank=True)
    permanent_city = models.CharField(max_length=100, null=True, blank=True)
    permanent_state = models.CharField(max_length=100, null=True, blank=True)
    permanent_pincode = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES)
    profile_links = models.JSONField(null=True, blank=True)  # Stores LinkedIn, GitHub, etc.

    def __str__(self):
        return self.emp_name
    

class EmpEducation(AuditModel):

    emp_name = models.CharField(max_length=255)
    emp_code = models.CharField(max_length=50, unique=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="educations")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emp_educations")
    user_master = models.ForeignKey(UserMaster, on_delete=models.CASCADE, related_name="emp_educations")
    company_master = models.ForeignKey(CompanyMaster, on_delete=models.CASCADE)
    ssc_grade = models.CharField(max_length=20, null=True, blank=True)
    ssc_img = models.CharField(max_length=255, null=True, blank=True)
    hsc_grade = models.CharField(max_length=20, null=True, blank=True)
    hsc_img = models.CharField(max_length=255, null=True, blank=True)
    ug_grade = models.CharField(max_length=20, null=True, blank=True)
    ug_img = models.CharField(max_length=255, null=True, blank=True)
    pg_grade = models.CharField(max_length=20, null=True, blank=True)
    pg_img = models.CharField(max_length=255, null=True, blank=True)
    other1_name = models.CharField(max_length=100, null=True, blank=True)
    other1_grade = models.CharField(max_length=20, null=True, blank=True)
    other1_img = models.CharField(max_length=255, null=True, blank=True)
    other2_name = models.CharField(max_length=100, null=True, blank=True)
    other2_grade = models.CharField(max_length=20, null=True, blank=True)
    other2_img = models.CharField(max_length=255, null=True, blank=True)
    verified_status = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.emp_name




class EmpAttendance(AuditModel):
    ATTENDANCE_STATUS_CHOICES = [
        ("Absent", "Absent"),
        ("Present-Office", "Present - Office"),
        ("Present-Home", "Present - Home"),
        ("Leave-Full Day", "Leave - Full Day"),
        ("Leave-Half Day", "Leave - Half Day"),
        ("Festival & Flexi Holiday", "Festival & Flexi Holiday"),
        ("Shift One", "Shift One"),
        ("Shift Two", "Shift Two"),
        ("Special Granted Conditional Leave", "Special Granted Conditional Leave"),
        ("Present-Business Tour", "Present - Business Tour"),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="emp_id")
    user_master = models.ForeignKey(UserMaster, on_delete=models.CASCADE, related_name="usermaster_id")
    company_master = models.ForeignKey(CompanyMaster, on_delete=models.CASCADE)
    emp_name = models.CharField(max_length=255)
    status = models.CharField(max_length=90, choices=ATTENDANCE_STATUS_CHOICES, default="Absent")

    check_in = models.BigIntegerField(null=True, blank=True)
    check_in_cords = models.CharField(max_length=100, null=True, blank=True)
    check_in_ip = models.CharField(max_length=100, null=True, blank=True)
    check_out = models.BigIntegerField(null=True, blank=True)
    check_out_cords = models.CharField(max_length=100, null=True, blank=True)
    check_out_ip = models.CharField(max_length=100, null=True, blank=True)
    remark = models.TextField(null=True, blank=True)
    approved_by = models.ForeignKey(UserMaster, on_delete=models.CASCADE, related_name="usermasterid")


    def __str__(self):
        check_in_date = datetime.fromtimestamp(self.check_in).date() if self.check_in else 'No Date'
        return f"{self.emp_name} - {self.status} ({check_in_date})"