from decouple import config
from django.core.cache import caches
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from api.my_auth.models import User
from tests.my_auth import credentials


class UserTests(APITestCase):
    signup_data = credentials.signup
    setUp_data = credentials.setUp_login
    login_data = credentials.login

    def test_signup_user(self):
        """
        Ensure we can create a new user object.
        """
        url = reverse('signup')
        data = self.signup_data  # valid request data

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("code"), "redirectToLogin")

        data.pop("password")  # --> valid response data, but invalid request data
        self.assertEqual(response.data.get("user"), data)
        self.assertEqual(User.objects.get(username=data.get("username")).username, data.get("username"))
        ...
        response = self.client.post(url, data, format='json')  # request with invalid data --> data with error messages

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("username")[0].title().lower(), "user with this username already exists.")
        self.assertEqual(response.data.get("email")[0].title().lower(), "user with this email already exists.")
        ...

    def setUp(self):
        self.user = User.objects.create_user(**self.setUp_data)

    def test_login_user(self):
        url = reverse("login")
        data = self.login_data
        response = self.client.post(url, data, format='json')
        refresh_token = RefreshToken(response.cookies["refresh"].value)
        access_token = AccessToken(response.data.get("access_token"))
        user = User.objects.get(email=data.get("username"))
        user_id = user.user_id
        token = user.outstandingtoken_set.filter(jti=refresh_token.payload.get("jti"))
        ...
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(access_token.payload.get("user_id"), user_id)
        self.assertEqual(len(token), 1)  # refresh --> outstanding_tokens in db
        ...


class TokenTests(APITestCase):
    setUp_logout = credentials.setUp_logout

    def setUp(self):
        self.user = User.objects.create_user(**self.setUp_logout)
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = self.refresh_token.access_token
        self.cache = caches["default"]

    def test_logout(self):
        url = reverse("logout")
        headers = credentials.headers
        headers.update({"Authorization": f"{config("SECRET")} {self.access_token}"})

        self.client.cookies["refresh"] = self.refresh_token
        self.client.headers = headers

        response = self.client.post(path=url, headers=headers, format='json')
        token_id = self.user.outstandingtoken_set.filter(jti=self.refresh_token.payload.get("jti"))[0].id
        is_blacklist = BlacklistedToken.objects.filter(token_id=token_id)

        # We need to check that refresh token in the blacklist
        self.assertEqual(bool(is_blacklist), True)

        # We need to check that access token in the blacklist (redis-cache)...
        self.assertEqual(str(self.access_token) in self.cache.get("accessBlacklist"), True)

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "Remove access token from local storage!")
        self.assertEqual(response.data.get("code"), "redirectToLogin")

    def test_refresh(self):
        ...
