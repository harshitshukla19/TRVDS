from django.contrib import admin
from .models import Evidence, FIR, Challan, Profile

# 1. Customize how Evidence (Uploaded Data) looks in Admin
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'violation_type', 'status', 'uploaded_at', 'is_fake')
    list_filter = ('status', 'violation_type', 'is_fake')
    search_fields = ('user__username', 'location')
    readonly_fields = ('uploaded_at',)

# 2. Customize how Profiles (User Info) look
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'avatar', 'phone', 'coins', 'certificate_unlocked')
    search_fields = ('user__username', 'phone')

# 3. Customize Challans
class ChallanAdmin(admin.ModelAdmin):
    list_display = ('vehicle_number', 'violator_name', 'amount', 'status', 'date')
    list_filter = ('status',)
    search_fields = ('vehicle_number',)

# 4. Register them so they appear in the Admin Panel
admin.site.register(Evidence, EvidenceAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Challan, ChallanAdmin)
admin.site.register(FIR)
