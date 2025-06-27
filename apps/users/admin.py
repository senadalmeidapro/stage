from django.contrib import admin
from .models import UserType, NurseryAssistant


admin.site.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = [
        field.name for field in UserType._meta.get_fields() 
        if not (field.many_to_many or field.one_to_many)
    ]    
    search_fields = ('user__username', 'contact', 'address')
    list_filter = ('type', 'is_actif')
    ordering = ('user__username',)


admin.site.register(NurseryAssistant)
class NurseryAssistantAdmin(admin.ModelAdmin):
    list_display = [
        field.name for field in NurseryAssistant._meta.get_fields() 
        if not (field.many_to_many or field.one_to_many)
    ]   
    search_fields = ('profil__user__username', 'nursery__name', 'classroom__name', 'group__name')
    list_filter = ('is_manager',)
    ordering = ('profil__user__username',)  
