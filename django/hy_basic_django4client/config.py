# configure django with jwt and whitenoise
import os


def configure_cors(settings, cors_allowed_origins=None, csrf_trusted_origins=None, allowed_hosts=None):
    if not hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
        settings.CORS_ALLOWED_ORIGINS = cors_allowed_origins or []
    elif cors_allowed_origins:
        settings.CORS_ALLOWED_ORIGINS.extend(cors_allowed_origins)

    if not hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
        settings.CSRF_TRUSTED_ORIGINS = csrf_trusted_origins or []
    elif csrf_trusted_origins:
        settings.CSRF_TRUSTED_ORIGINS.extend(csrf_trusted_origins)

    if not hasattr(settings, 'ALLOWED_HOSTS'):
        settings.ALLOWED_HOSTS = allowed_hosts or []
    elif allowed_hosts:
        settings.ALLOWED_HOSTS.extend(allowed_hosts)


def configure_django(settings):
    """
    Configure Django settings for JWT authentication and Whitenoise.
    """
    from datetime import timedelta
    
    # make sure rest framework is configured
    if 'rest_framework' not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS.append('rest_framework')
        settings.INSTALLED_APPS.append('rest_framework.authtoken')
        settings.REST_FRAMEWORK = { 
            'DEFAULT_RENDERER_CLASSES': [ 
                'rest_framework.renderers.JSONRenderer', 
                'rest_framework.renderers.BrowsableAPIRenderer', 
            ], 

            'DEFAULT_PARSER_CLASSES': [ 
                'rest_framework.parsers.FormParser', 
                'rest_framework.parsers.MultiPartParser', 
                'rest_framework.parsers.JSONParser', 
            ], 

            'DEFAULT_AUTHENTICATION_CLASSES': [ 
                'rest_framework_simplejwt.authentication.JWTAuthentication', 
                'rest_framework.authentication.SessionAuthentication', 
                'rest_framework.authentication.TokenAuthentication', 
            ], 

            'DEFAULT_PERMISSION_CLASSES': ( 
                'rest_framework.permissions.IsAuthenticated', 
            ), 
        }
    
    # handle cors and csrf
    if 'corsheaders' not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS.append('corsheaders')
    if 'corsheaders.middleware.CorsMiddleware' not in settings.MIDDLEWARE:
        settings.MIDDLEWARE.insert(settings.MIDDLEWARE.index('django.middleware.common.CommonMiddleware'), 'corsheaders.middleware.CorsMiddleware')
    if 'django.middleware.csrf.CsrfViewMiddleware' not in settings.MIDDLEWARE:
        settings.MIDDLEWARE.insert(settings.MIDDLEWARE.index('django.middleware.common.CommonMiddleware') + 1, 'django.middleware.csrf.CsrfViewMiddleware')

    if not hasattr(settings, 'CSRF_COOKIE_PATH'):
        settings.CSRF_COOKIE_PATH = '/'
    if not hasattr(settings, 'SESSION_COOKIE_PATH'):
        settings.SESSION_COOKIE_PATH = '/'

    # JWT REST FRAMEWORK
    if 'rest_framework_simplejwt' not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS.append('rest_framework_simplejwt')
        settings.INSTALLED_APPS.append('rest_framework_simplejwt.token_blacklist') # needed for logout' 

    # Whitenoise
    if 'whitenoise.runserver_nostatic' not in settings.INSTALLED_APPS:
        # add it after django.contrib.messages
        settings.INSTALLED_APPS.insert(settings.INSTALLED_APPS.index('django.contrib.messages') + 1, 'whitenoise.runserver_nostatic')
    
    # Add middleware for Whitenoise
    if 'whitenoise.middleware.WhiteNoiseMiddleware' not in settings.MIDDLEWARE:
        settings.MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    
    # Configure JWT
    # add jwt auth if nto already added
    if 'rest_framework_simplejwt.authentication.JWTAuthentication' not in settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']:
        settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'].append('rest_framework_simplejwt.authentication.JWTAuthentication')
    # add permission if not already added
    if 'rest_framework.permissions.IsAuthenticated' not in settings.REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES']:
        settings.REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'].append('rest_framework.permissions.IsAuthenticated')
    
    settings.JWT_EXPIRATION_DELTA = timedelta(minutes=60) 
    settings.SIMPLE_JWT = {
        # Lifetime of the access token 
        'ACCESS_TOKEN_LIFETIME': settings.JWT_EXPIRATION_DELTA, 
        # Lifetime of the refresh token 
        'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=5), 
        'SLIDING_TOKEN_LIFETIME': timedelta(days=5), 

        # 'ROTATE_REFRESH_TOKENS': False,
        # 'BLACKLIST_AFTER_ROTATION': True,
        # 'ALGORITHM': 'HS256',
        # 'SIGNING_KEY': settings.SECRET_KEY,
        # 'VERIFYING_KEY': None,
        # 'AUTH_HEADER_TYPES': ('Bearer',),
        # 'USER_ID_FIELD': 'id',
        # 'USER_ID_CLAIM': 'user_id',
        # 'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
        # 'TOKEN_TYPE_CLAIM': 'token_type',
    }
    
    # Configure static files for Whitenoise
    if not hasattr(settings, 'STATIC_ROOT' ) or not settings.STATIC_ROOT:
        settings.STATIC_ROOT = os.path.join(settings.BASE_DIR.parent, 'static') 
        # check if the static folder exists and create it if not
        if not os.path.exists(settings.STATIC_ROOT):
            os.makedirs(settings.STATIC_ROOT)
    if not hasattr(settings, 'STATIC_URL') or not settings.STATIC_URL:
        settings.STATIC_URL = '/static/'

    # settings.STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
