from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken 
from django.contrib.auth import get_user_model 
from django.http import HttpResponseForbidden
from rest_framework.decorators import (authentication_classes, permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_403_FORBIDDEN
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import  csrf_exempt
from django.utils.decorators import method_decorator
import logging

LOGGER = logging.getLogger(__name__)

@authentication_classes([JWTAuthentication]) 
@permission_classes([IsAuthenticated]) 
class JWTModelViewset(viewsets.ModelViewSet):
    """
    JWT auth enabled rest framework viewset class, to be extended by other viewsets.
    """
    pass

class RESTAuthHandler:
    """
    Helper class for rest framework authentication.
    """
    @staticmethod 
    def getRestAuthenticatedUser(request): 
        """
            Use rest framework auth in normal views.
        """
        token_key = request.META.get("HTTP_AUTHORIZATION") 
        if token_key: 
            try: 
                # Attempt to fetch the user associated with the token 
                if token_key.startswith("Token "): 
                    token_key = token_key[6:] 
                if token_key.startswith("Bearer "): 
                    token_key = token_key[7:] 
                token = Token.objects.get(key=token_key) 
                user = token.user 
                return user 
            except Token.DoesNotExist: 
                return None 

class CrsfHandler:
    """
    Helper class for CSRF handling.
    """

    @staticmethod
    def get_csrf_token(request):
        """
        Get CSRF token.
        """
        from django.middleware.csrf import get_token
        token = get_token(request)
        return JsonResponse({'csrfToken': token})

@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response({'error': 'Please provide username and password.'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        LOGGER.warning(f"Unable to login with user '{username}'")
        return Response({'error': 'Invalid Credentials'}, status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'id': user.id}, status=HTTP_200_OK)

@api_view(["GET"])
@method_decorator(csrf_exempt, name='dispatch')
@permission_classes((IsAuthenticated,))
def get_csrf_token(request):
    return CrsfHandler.get_csrf_token(request)

class JWTAuthHandler:
    """
    JWT helper class for Django views.

    Check django views like:

    def myview(request): 
        user = JWTAuthHandler.verify_jwt_token_from_request(request) 
        if not user: 
            return JWTAuthHandler.get_error_result() 
    """

    def __init__(self, request):
        """
        Initialize JWT handler.
        """
        self.request = request

    def get_token(self):
        """
        Get JWT token from request.
        """
        token = JWTAuthentication().get_validated_token(self.request)
        return token

    @staticmethod 
    def verify_jwt_token(token) -> User: 
        try: 
            access_token = AccessToken(token) 
            user_id = access_token['user_id'] 
            User = get_user_model() 
            user = User.objects.get(pk=user_id) 
            return user 
        except Exception as e: 
            return None # Token is not valid or expired 

    @staticmethod 
    def verify_jwt_token_from_request(request) -> User: 
        token = request.META.get('HTTP_AUTHORIZATION', '').split('Bearer ')[-1].strip() 
        if token: 
            return JWTAuthHandler.verify_jwt_token(token) 
        return None 

    @staticmethod 
    def get_error_result(): 
        return HttpResponseForbidden('Unauthorized') 

    def get_user(self) -> User:
        """
        Get user from JWT token.
        """
        token = self.get_token()
        user = token.user
        return user

    def get_user_id(self):
        """
        Get user id from JWT token.
        """
        user = self.get_user()
        user_id = user.id
        return user_id

    def get_user_email(self):
        """
        Get user email from JWT token.
        """
        user = self.get_user()
        user_email = user.email
        return user_email

    def get_user_username(self):
        """
        Get user username from JWT token.
        """
        user = self.get_user()
        user_username = user.username
        return user_username

    def get_user_full_name(self):
        """
        Get user full name from JWT token.
        """
        user = self.get_user()
        user_full_name = user.get_full_name()
        return user_full_name

    def get_user_first_name(self):
        """
        Get user first name from JWT token.
        """
        user = self.get_user()
        user_first_name = user.first_name
        return user_first_name

    def get_user_last_name(self):
        """
        Get user last name from JWT token.
        """
        user = self.get_user()
        user_last_name = user.last_name
        return user_last_name

    def get_user_is_active(self):
        """
        Get user is active from JWT token.
        """
        user = self.get_user()
        user_is_active = user.is_active
        return user_is_active

    def get_user_is_staff(self):
        """
        Get user is staff from JWT token.
        """
        user = self.get_user()
        user_is_staff = user.is_staff
        return user_is_staff

    def get_user_is_superuser(self):
        """
        Get user is superuser from JWT token.
        """
        user = self.get_user()
        user_is_superuser = user.is_superuser
        return user_is_superuser

    @staticmethod
    def configure_urls(urlpatterns):
        """
        Configure Django urlpatterns for JWT authentication.
        """
        from django.urls import path
        from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

        # add jwt urls if not already added
        if 'rest_framework_simplejwt.views.TokenObtainPairView' not in urlpatterns:
            urlpatterns.append(path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'))
        if 'rest_framework_simplejwt.views.TokenRefreshView' not in urlpatterns:
            urlpatterns.append(path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'))
        if 'rest_framework_simplejwt.views.TokenVerifyView' not in urlpatterns:
            urlpatterns.append(path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'))
        if 'api/login/' not in urlpatterns:
            urlpatterns.append(path('api/login/', login, name='login'))
        if 'api/csrf/' not in urlpatterns:
            urlpatterns.append(path('api/csrf/', get_csrf_token, name='csrf'))



