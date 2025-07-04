from django.contrib import admin
from .models import Nursery, OpeningHour, NurseryAssistant

class OpeningHourInline(admin.TabularInline):
    model = OpeningHour
    extra = 7  # Un formulaire pour chaque jour de la semaine
    max_num = 7  # Maximum 7 jours
    can_delete = False

class NurseryAssistantInline(admin.TabularInline):
    model = NurseryAssistant
    extra = 1
    raw_id_fields = ('profil', 'classroom', 'group')
    fields = ('profil', 'classroom', 'group', 'is_manager', 'active')
    show_change_link = True

@admin.register(Nursery)
class NurseryAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'contact_number', 'verified', 'online')
    list_filter = ('verified', 'online', 'legal_status')
    search_fields = ('name', 'address', 'contact_number')
    readonly_fields = ('upload_folder', 'created_at', 'updated_at')
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'manager', 'address', 'contact_number', 'information')
        }),
        ('Capacité', {
            'fields': ('max_age', 'max_children_per_class')
        }),
        ('Statut légal', {
            'fields': ('legal_status', 'verified', 'online')
        }),
        ('Documents', {
            'fields': ('agreement_document', 'id_card_document')
        }),
        ('Photos', {
            'fields': ('photo_exterior', 'photo_interior')
        }),
        ('Métadonnées', {
            'fields': ('upload_folder', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [OpeningHourInline, NurseryAssistantInline]

@admin.register(OpeningHour)
class OpeningHourAdmin(admin.ModelAdmin):
    list_display = ('nursery', 'get_day_display', 'open_time', 'close_time', 'is_closed')
    list_filter = ('day', 'is_closed')
    search_fields = ('nursery__name',)
    list_select_related = ('nursery',)

    def get_day_display(self, obj):
        return obj.get_day_display()
    get_day_display.short_description = 'Jour'

@admin.register(NurseryAssistant)
class NurseryAssistantAdmin(admin.ModelAdmin):
    list_display = ('profil', 'nursery', 'classroom', 'group', 'is_manager', 'active')
    list_filter = ('nursery', 'is_manager', 'active')
    search_fields = ('profil__user__username', 'profil__user__email', 'nursery__name')
    raw_id_fields = ('profil', 'nursery', 'classroom', 'group')
    list_select_related = ('profil', 'nursery', 'classroom', 'group')
