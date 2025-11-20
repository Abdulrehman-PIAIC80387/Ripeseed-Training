from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils import timezone
import json
from licensing.models import Organization, License, LicenseHistory
from licensing.services import LicenseService, RefundService
from common.utils import *


class LicenseInline(admin.StackedInline):
    model = License
    extra = 0
    max_num = 1
    fields = ('start_date', 'end_date', 'seat_cap', 'seat_price', 'is_active')


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact_number', 'created_at')
    search_fields = ('name', 'email')
    inlines = [LicenseInline]


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('organization', 'start_date', 'end_date', 'seat_cap', 
                    'seat_price', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('organization__name',)
    readonly_fields = ('refund_breakdown_display',)
    actions = ['renew_licenses', 'deactivate_licenses','increase_seats','decrease_seats','update_price']
    
    fieldsets = (
        ('License Details', {
            'fields': ('organization', 'start_date', 'end_date', 'seat_cap', 'seat_price', 'is_active')
        }),
        ('Refund Breakdown', {
            'fields': ('refund_breakdown_display',),
        }),
    )
    
    def refund_breakdown_display(self, obj):
        if not obj.pk:
            return "Save the license first to see refund calculation"
        
        if not obj.is_active:
            return "License is inactive - no refund applicable"
        
        refund_data = RefundService.calculate_refund(obj)
        
        return format_html('<pre>{}</pre>', json.dumps(refund_data, indent=2, default=str))
    
    refund_breakdown_display.short_description = _('Refund Breakdown by Actions')
    

    @admin.action(description=_('Renew selected licenses (12 months)'))
    def renew_licenses(self, request, queryset):
        for license_obj in queryset:
            try:
                LicenseService.renew_license(license_obj, performed_by=parse_admin_user(request))
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        
            messages.success(request, f"Renewed {queryset.count()} license(s)")


    @admin.action(description=_('Deactivate selected licenses'))
    def deactivate_licenses(self, request, queryset):
        for license_obj in queryset:
            try:
                LicenseService.deactivate_license(license_obj,performed_by=parse_admin_user(request))
                
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        messages.success(request, f"Deactivated {queryset.count()} license(s)")
        
        
    @admin.action(description=_('Increase seats by 10'))
    def increase_seats(self, request, queryset):
        for license_obj in queryset:
            try:
                LicenseService.increase_seat_capacity(license_obj,seats_to_add=10,
                performed_by=parse_admin_user(request))
            
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
                
        messages.success(request, f"Increased seats for {queryset.count()} license(s)")


    @admin.action(description=_('Decrease seats by 10'))
    def decrease_seats(self, request, queryset):
        for license_obj in queryset:
            try:
                LicenseService.decrease_seat_capacity(license_obj,seats_to_remove=10,performed_by=parse_admin_user(request))

            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        
        messages.success(request, f"Decreased seats for {queryset.count()} license(s)")


    @admin.action(description=_('Update seat price to $20'))
    def update_price(self, request, queryset):
        new_price = 20  
        for license_obj in queryset:
            try:
                LicenseService.update_seat_price(license_obj,new_price=new_price,performed_by=parse_admin_user(request))
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        
        messages.success(request, f"Updated price to ${new_price} for {queryset.count()} license(s)")


@admin.register(LicenseHistory)
class LicenseHistoryAdmin(admin.ModelAdmin):
    list_display = ('license', 'action', 'performed_by', 'refund_amount', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('license__organization__name', 'performed_by')