from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

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
                    'seat_price', 'monthly_cost_display', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('organization__name',)
    readonly_fields = ('refund_info_display',)
    actions = ['renew_licenses', 'deactivate_licenses']
    
    fieldsets = (
        ('License Details', {
            'fields': ('organization', 'start_date', 'end_date', 'seat_cap', 
                      'seat_price', 'is_active')
        }),
        ('Refund Information', {
            'fields': ('refund_info_display',),
        }),
    )


    def monthly_cost_display(self, obj):
        return format_currency(get_license_monthly_cost(obj))
    monthly_cost_display.short_description = _('Monthly Cost')
    
    
    def refund_info_display(self, obj):
        if not obj.pk:
            return "Save the license first to see refund calculation"
        
        if not obj.is_active:
            return "License is inactive - no refund applicable"
        
        refund_amount = RefundService.calculate_refund(obj)
        days_remaining = get_license_days_remaining(obj)
        total_days = get_license_duration_days(obj)
        days_used = total_days - days_remaining
        
        if refund_amount == 0:
            return "No refund applicable (license expired)"
        
        usage_percent = (days_used / total_days * 100) if total_days > 0 else 0
        
        return format_html(
            '<strong>Days Used:</strong> {} of {} days ({:.1f}%)<br>'
            '<strong>Days Remaining:</strong> {} days<br>'
            '<strong>Refund Amount:</strong> <span style="color: green; font-size: 14px;">{}</span>',
            days_used, total_days, usage_percent,
            days_remaining,
            format_currency(refund_amount)
        )
    refund_info_display.short_description = _('Refund Calculation')


    @admin.action(description=_('Renew selected licenses (12 months)'))
    def renew_licenses(self, request, queryset):
        for license_obj in queryset:
            try:
                LicenseService.renew_license(license_obj, performed_by=parse_admin_user(request))
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        
            messages.success(request, f"Renewed {len(queryset)} license(s)")


    @admin.action(description=_('Deactivate selected licenses'))
    def deactivate_licenses(self, request, queryset):
        for license_obj in queryset:
            try:
                refund = LicenseService.deactivate_license(license_obj,performed_by=parse_admin_user(request))
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        messages.success(request, f"Deactivated {len(queryset)} license(s)")


@admin.register(LicenseHistory)
class LicenseHistoryAdmin(admin.ModelAdmin):
    list_display = ('license', 'action', 'performed_by', 'refund_amount', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('license__organization__name', 'performed_by')
    
    