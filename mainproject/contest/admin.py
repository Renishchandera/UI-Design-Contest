from django.contrib import admin
from .models import User, Contest, Submission, Participation

# Register User model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'coins', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')

# Register Contest model
@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'entry_fee', 'limit')
    search_fields = ('title',)

# Register Submission model
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'contest_id', 'votes')
    search_fields = ('user_id__username', 'contest_id__title')

# Register Participation model
@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'contest_id', 'registered_at', 'status')
    search_fields = ('user_id__username', 'contest_id__title')
