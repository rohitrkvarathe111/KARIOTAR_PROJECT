from django.contrib import admin
from .models import Employee, EmpProfile, EmpEducation, EmpAttendance
# Register your models here.

class EmployeeTable(admin.ModelAdmin):
    list_display = ('id', 'emp_name')  
    search_fields = ('emp_name',)

class EmpProfileTable(admin.ModelAdmin):
    list_display = ('id', 'emp_name', 'emp_code')  
    search_fields = ('emp_name',)

class EmpEducationTable(admin.ModelAdmin):
    list_display = ('id', 'emp_name', 'emp_code')  
    search_fields = ('emp_name',)

class EmpAttendanceTable(admin.ModelAdmin):
    list_display = ('id', 'emp_name', 'check_in', 'check_out',)    
    search_fields = ('emp_name',)

admin.site.register(Employee, EmployeeTable)
admin.site.register(EmpProfile, EmpProfileTable)
admin.site.register(EmpEducation, EmpEducationTable)
admin.site.register(EmpAttendance, EmpAttendanceTable)