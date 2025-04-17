from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register_company_employee', views.register_company_employee, name='register_company_employee'),
    path('get_registered_employee', views.get_registered_employee, name='get_registered_employee'),
    path('update_emp_details/<int:emp_id>', views.update_emp_details, name='edit_employee_details'),
    path('update_emp_profile/<int:emp_id>', views.update_emp_profile, name='edit_employee_profile'),
    path('update_emp_education/<int:emp_id>', views.update_emp_education, name='edit_employee_profile'),
    path('verified_emp/<int:emp_id>', views.verified_emp, name='verified_emp'),
    path('checkin_attendance', views.checkin_attendance, name='mark_attendance'),
]