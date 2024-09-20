from api.custom_auth.models import User
from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenBlacklistSerializer
from typing import Dict, Any


class CustomRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        refresh_str = attrs["refresh"]
        refresh_obj = self.token_class(refresh_str)
        user_id = refresh_obj.payload["user_id"]
        user = User.objects.filter(pk=user_id).prefetch_related()
        # print(user[0].outstandingtoken_set.values())
        refresh_token = self.token_class.for_user(user[0])
        data = {"access": str(refresh_token.access_token)}

        # The code below is from SimpleJWT default TokenRefreshSerializer
        if settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"]:
            if settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"]:
                try:
                    # Attempt to blacklist the given old refresh token
                    refresh_obj.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            data["refresh"] = str(refresh_token)
        return data


class CustomBlacklistSerializer(TokenBlacklistSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[Any, Any]:
        refresh = self.token_class(attrs["refresh"])
        try:
            refresh.blacklist()
        except AttributeError:
            pass
        return {
            "detail": "Successful logging out!",
            "code": "redirectToLogin",
            "message": "Remove access token from local storage!"
        }


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        # extra_kwargs = {"password": {"write_only": True}}
    
    def create(self, validated_data):        
        user = super().create(validated_data=validated_data)
        user.set_password(validated_data.get("password"))
        user.save()
        return user


class LoginExtraDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["last_login", "last_login_IP"]
    