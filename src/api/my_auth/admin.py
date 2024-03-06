from django.contrib import admin
from api.my_auth.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["user_id", "username", "last_login_IP", "is_active"]
    ordering = "user_id",