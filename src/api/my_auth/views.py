from api.my_auth.serializers import (
    UserSerializer, LoginExtraDataSerializer, CustomRefreshSerializer, CustomBlacklistSerializer
)
from api.my_auth.utils import check_access_token
from django.contrib.auth import authenticate
from django.conf import settings
from django.core.cache import caches
from django.utils import timezone
from rest_framework import status, permissions, renderers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken


class TestView(APIView):
    """Simple Test view class"""
    permission_classes = [permissions.IsAuthenticated]
    cache = caches["default"]

    def get(self, request):
        if not check_access_token(token=str(request.auth), cache=self.cache):
            return Response(
                {
                    "detail": "User is logged out. Access token was blacklisted!",
                    "code": "redirectToLogin"}, status=status.HTTP_400_BAD_REQUEST
                )
        return Response({"message": "Authentication works!", "user": str(request.user)})


class CustomRefreshView(APIView):
    """Custom Refresh view with setting refresh_token as httpOnly cookie.
    * In regular behavior we set refresh_token at client local_storage."""
    serializer_class = CustomRefreshSerializer
    renderer_classes = [renderers.JSONRenderer]

    def post(self, request) -> Response:
        refresh_token = request.META.get("HTTP_COOKIE").split("=")[-1]  # --> str
        data = {"refresh": refresh_token}
        serializer = self.serializer_class(data=data)

        try:
            serializer.is_valid(raise_exception=True)
            # We do not need to send token with access token. We need add it to httpOnly cookie!
            refresh = serializer.validated_data.pop("refresh")
            response = Response(serializer.validated_data, status=status.HTTP_200_OK)
            response.set_cookie(
                key="refresh", value=refresh, path="/api/auth/",
                expires=settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME"), httponly=True
            )
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return response


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.JSONRenderer]
    serializer_class = CustomBlacklistSerializer
    cache = caches["default"]

    def post(self, request) -> Response:
        # We need get refresh token from httponly cookie, not request.data!
        refresh_token = request.META.get("HTTP_COOKIE").split("=")[-1]  # --> str
        access_token = str(request.auth)
        data = {"refresh": refresh_token}
        serializer = self.serializer_class(data=data)

        # We also need to add access token to blacklist and delete from client storage after logging out...
        if access_token:
            # because even if refresh token is blacklisted, access token have the power until it will be expired
            set_data = self.cache.get("accessBlacklist")

            if set_data is None:
                set_data = set()
            set_data.add(access_token)
            self.cache.set('accessBlacklist', set_data, 3600)

        # The code below is from SimpleJWT default BlackListView
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LoginView(APIView):
    serializer_class = LoginExtraDataSerializer
    renderer_classes = [renderers.JSONRenderer]
    cache = caches["default"]

    def post(self, request):
        if str(request.user) == "AnonymousUser":
            user = authenticate(username=request.data.get("username"), password=request.data.get("password"))
            if not user:
                return Response({"detail": "Wrong username or password!"}, status=status.HTTP_401_UNAUTHORIZED)

            # Each new login, new JWT tokens pair is generating
            refresh_token = RefreshToken.for_user(user)  # --> outstanding token table
            access_token = refresh_token.access_token

            # Also collect some extra data
            extra_data = {}
            
            if user.check_password(request.data.get("password")):
                extra_data["last_login"] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                extra_data["last_login_IP"] = request.META.get("REMOTE_ADDR")
                ...

            serializer = self.serializer_class(instance=user, data=extra_data)

            if serializer.is_valid():
                serializer.save()
                # Send access token via json data
                response = Response(
                    {"access_token": str(access_token)}, status=status.HTTP_200_OK
                )
                # Set refresh_token to httpOnly cookie on a client
                response.set_cookie(
                    key="refresh", value=refresh_token, path="/api/auth/",
                    expires=settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME"), httponly=True
                    )
                return response
            return Response(serializer.errors)
        else:
            if not check_access_token(token=str(request.auth), cache=self.cache):
                return Response(
                    {"detail": "User is logged out. Access token was blacklisted!",
                     "code": "redirectToLogin"}, status=status.HTTP_400_BAD_REQUEST
                )
            # When user with valid access token tries to login, we need to generate the message to client...
            user_data = UserSerializer(instance=request.user).data
            return Response({"detail": "You are already logged in!", "code": "userLoggedIn", "user": user_data})


class SignupView(APIView):
    serializer_class = UserSerializer
    renderer_classes = [renderers.JSONRenderer]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "user": serializer.data,
                    "code": "redirectToLogin",
                    "status": status.HTTP_201_CREATED
                    },
                status=status.HTTP_201_CREATED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
