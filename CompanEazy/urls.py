from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register_company_employee', views.register_company_employee, name='register_company_employee'),
]