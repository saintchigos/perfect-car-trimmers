from django.contrib import admin
from django.shortcuts import redirect

from .models import Booking, FabricOption, GalleryItem, SiteContent, TimeSlot


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    """Singleton admin: always redirects straight to editing the one row,
    so business owners never see a confusing empty list or 'Add another'."""

    fieldsets = (
        ("Hero Section", {
            'fields': ('hero_heading', 'hero_heading_accent', 'hero_subheading', 'hero_banner_image'),
        }),
        ("Google Rating Badge", {
            'fields': ('show_google_rating', 'google_rating', 'google_review_count', 'google_review_url'),
        }),
        ("About Section", {
            'fields': ('about_heading', 'about_text', 'about_image'),
        }),
    )

    def has_add_permission(self, request):
        return not SiteContent.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteContent.load()
        return redirect('admin:bookings_sitecontent_change', obj.pk)


@admin.register(FabricOption)
class FabricOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'extra_cost', 'is_active')
    list_editable = ('is_active',)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'end_time', 'slot_type', 'capacity', 'bookings_count', 'is_full')
    list_filter = ('slot_type', 'date')
    ordering = ('date', 'start_time')


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ('vehicle_type', 'caption', 'featured', 'created_at')
    list_editable = ('featured',)
    list_filter = ('featured', 'vehicle_type')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'customer_name', 'phone_number', 'vehicle_make', 'timeslot',
        'service_mode', 'status', 'deposit_paid', 'created_at',
    )
    list_editable = ('status',)
    list_filter = ('status', 'service_mode', 'deposit_required', 'deposit_paid')
    search_fields = ('customer_name', 'phone_number', 'vehicle_make', 'vehicle_model')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
