# from django.contrib import admin
# from .models import Nursery, OpeningHour
# # Register your models here.
# admin.site.register(Nursery)
# class NurseryAdmin(admin.ModelAdmin):
#     list_display = [
#         field.name for field in Nursery._meta.get_fields() 
#         if not (field.many_to_many or field.one_to_many)
#     ]   
#     search_fields = ('name', 'address', 'contact_number')
#     list_filter = ('created_at', 'updated_at')
#     ordering = ('name',)

# admin.site.register(OpeningHour)
# class OpeningHourAdmin(admin.ModelAdmin):
#     list_display = [
#         field.name for field in OpeningHour._meta.get_fields() 
#         if not (field.many_to_many or field.one_to_many)
#     ]   
#     search_fields = ('nursery__name',)
#     list_filter = ('day_of_week',)
#     ordering = ('nursery__name',)

