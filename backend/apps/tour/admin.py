from django.contrib import admin

from .models import TouristSession, TourRating, KioskPin

__all__ = ("TouristSessionAdmin", "TourRatingAdmin", "KioskPinAdmin")


@admin.register(TouristSession)
class TouristSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "device_token", "device_name", "ip_address", "tour_number", "tour_session", "is_active", "joined_at", "left_at", "created_at")
    list_filter = ("is_active", "tour_session")
    readonly_fields = ("created_at", "joined_at", "left_at")
    search_fields = ("device_token", "device_name", "ip_address")
    raw_id_fields = ("tour_session",)


@admin.register(TourRating)
class TourRatingAdmin(admin.ModelAdmin):
    list_display = ("id", "tourist_session", "rating", "comment", "created_at")
    list_filter = ("rating",)
    readonly_fields = ("tourist_session", "created_at")
    search_fields = ("comment",)


@admin.register(KioskPin)
class KioskPinAdmin(admin.ModelAdmin):
    list_display = ("code", "updated_at")

    def has_add_permission(self, request):
        # Только одна запись
        if KioskPin.objects.exists():
            return False
        return super().has_add_permission(request)

