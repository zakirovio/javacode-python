from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/auth/", include("api.custom_auth.urls")),
    path("api/v1/", include("api.v1.wallet.urls"))
]
