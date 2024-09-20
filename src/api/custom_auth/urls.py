from api.custom_auth.views import LoginView, SignupView, TestView, LogoutView, CustomRefreshView
from django.urls import path


urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', CustomRefreshView.as_view(), name='refresh'),
    path("test/", TestView.as_view(), name="test"),
]
