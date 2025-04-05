from django.contrib import admin
from .models import UserType, CompanyMaster, UserMaster, MenuMaster
from django.contrib.sessions.models import Session


class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_type')  
    search_fields = ('user_type',)  

class CompanyMasterAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name', 'created_at', 'main_role_id')  
    search_fields = ('company_name',)
    list_filter = ('created_at',)

class UserMasterAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'unique_username', 'email')  
    search_fields = ('first_name', 'unique_username', 'email')

class MenuMasterAdmin(admin.ModelAdmin):
    list_display = ('subrole_id', 'sub_role', 'main_role')
    search_fields = ('main_role', 'sub_role')

class SessionMasterAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'expire_date')
    search_fields = ('expire_date',)

admin.site.register(Session, SessionMasterAdmin)
admin.site.register(UserType, UserTypeAdmin)
admin.site.register(CompanyMaster, CompanyMasterAdmin)
admin.site.register(UserMaster, UserMasterAdmin)
admin.site.register(MenuMaster, MenuMasterAdmin)
