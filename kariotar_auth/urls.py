from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('user_comapny_helper/<str:type>', views.user_comapny_helper, name='user_comapny_helper'),
    path('register_company', views.register_company_with_CSA_user, name='register_company_with_CSA_user'),
    path('create_user_for_company', views.create_user_for_company, name='create_user_for_company'),
    path('user_login', views.User_login, name='User_login'),
    path('user_logout', views.User_logout, name='user_logout'),
    path('chnage_user_password', views.Chnage_user_password, name='Chnage_user_password'),
    path('user_data', views.User_data, name='User_data'),

]
