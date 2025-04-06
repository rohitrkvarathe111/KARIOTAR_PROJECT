# from django.db import models
# from kariotar_auth.models import User, CompanyMaster, UserMaster
# # Create your models here.



# class Employee(models.Model):
#     EMPLOYEE_TYPES = [
#         ('Full-Time', 'Full-Time'),
#         ('Part-Time', 'Part-Time'),
#         ('Contract', 'Contract'),
#         ('Intern', 'Intern'),
#         ('Freelancer', 'Freelancer'),
#         ('Temporary', 'Temporary'),
#         ('Consultant', 'Consultant'),
#         ('Apprentice', 'Apprentice'),
#         ('Volunteer', 'Volunteer'),
#         ('Seasonal', 'Seasonal'),
#         ('Probationary', 'Probationary'),
#         ('Remote', 'Remote'),
#         ]

#     emp_name = models.CharField(max_length=255)             # full name of user_master
#     company_master = models.ForeignKey(CompanyMaster, on_delete=models.CASCADE)
#     user_master = models.ForeignKey(UserMaster, on_delete=models.CASCADE)
#     user_id = models.ForeignKey(User, on_delete=models.CASCADE)
#     group = models.CharField(max_length=255)
#     emp_type = models.CharField(max_length=20, choices=EMPLOYEE_TYPES)
#     department = models.CharField(max_length=255)
#     position = models.CharField(max_length=255)
#     funt_manager = models.ForeignKey(UserMaster, on_delete=models.CASCADE)
#     admin_manager = models.ForeignKey(UserMaster, on_delete=models.CASCADE)
#     salary_lpa = models.BigIntegerField(default=0)         # salary in paisa format
#     date_joined = models.DateField()
#     is_active = models.BooleanField(default=True)
#     offer_letter = models.CharField(max_length=255, blank=True, null=True)
#     emp_agreement = models.CharField(max_length=255, blank=True, null=True)
#     nda = models.CharField(max_length=255, blank=True, null=True)
#     resignation = models.CharField(max_length=255, blank=True, null=True)
#     assets = models.TextField(blank=True, null=True)
#     leave_bal_pa = models.IntegerField()

#     def __str__(self):
#         return self.emp_name