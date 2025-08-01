# configure django with jwt and whitenoise
import os


def configure_cors(settings, hosts=[], ports=[]):
    """
    Configure Django settings for CORS and CSRF.

    :param settings: Django settings module.
    :param hosts: List of hosts to allow.
    :param ports: List of ports to allow.
    """
    if "[::1]" not in hosts:
        hosts.append("[::1]")
    if "django" not in hosts:
        hosts.append("django")

    cors_allowed_origins = []
    csrf_trusted_origins = []
    allowed_hosts = []
    for host in hosts:
        for port in ports:
            for h in ["http","https"]:
                cors_allowed_origins.append(f"{h}://{host}:{port}")
                csrf_trusted_origins.append(f"{h}://{host}:{port}")
                allowed_hosts.append(f"{host}")

    for host in hosts:
        for h in ["http","https"]:
            cors_allowed_origins.append(f"{h}://{host}")
            csrf_trusted_origins.append(f"{h}://{host}")

    if not hasattr(settings, 'ALLOWED_HOSTS'):
        settings.ALLOWED_HOSTS = []
    if not hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
        settings.CORS_ALLOWED_ORIGINS = []
    if not hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
        settings.CSRF_TRUSTED_ORIGINS = []

    if allowed_hosts:
        for host in allowed_hosts:
            if host not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append(host)
    if cors_allowed_origins:
        for origin in cors_allowed_origins:
            if origin not in settings.CORS_ALLOWED_ORIGINS:
                settings.CORS_ALLOWED_ORIGINS.append(origin)
    if csrf_trusted_origins:
        for origin in csrf_trusted_origins:
            if origin not in settings.CSRF_TRUSTED_ORIGINS:
                settings.CSRF_TRUSTED_ORIGINS.append(origin)


def configure_django(settings, jwt_expiration_delta_min:int=60, use_whitenoise:bool=False):
    """
    Configure Django settings for JWT authentication and Whitenoise.

    :param settings: Django settings module.
    """
    from datetime import timedelta
    
    # make sure rest framework is configured
    if 'rest_framework' not in settings.INSTALLED_APPS:
        index = lastDjangoIndex(settings)
        settings.INSTALLED_APPS.insert(index, 'rest_framework')
        settings.INSTALLED_APPS.insert(index+1, 'rest_framework.authtoken')
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
        index = lastDjangoIndex(settings)
        settings.INSTALLED_APPS.insert(index, 'corsheaders')
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
        # add after the last app that starts with 'django'
        index = lastDjangoIndex(settings)
        settings.INSTALLED_APPS.insert(index, 'rest_framework_simplejwt')
        settings.INSTALLED_APPS.insert(index+1, 'rest_framework_simplejwt.token_blacklist') # needed for logout' 
        
        

    if use_whitenoise:
        # Whitenoise
        if 'whitenoise.runserver_nostatic' not in settings.INSTALLED_APPS:
            # add it after django.contrib.messages
            settings.INSTALLED_APPS.insert(0, 'whitenoise.runserver_nostatic')
        
        # Add middleware for Whitenoise
        if 'whitenoise.middleware.WhiteNoiseMiddleware' not in settings.MIDDLEWARE:
            settings.MIDDLEWARE.insert(settings.MIDDLEWARE.index('django.middleware.security.SecurityMiddleware') + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    
    # Configure JWT
    # add jwt auth if not already added
    if 'rest_framework_simplejwt.authentication.JWTAuthentication' not in settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']:
        settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'].append('rest_framework_simplejwt.authentication.JWTAuthentication')
    # add permission if not already added
    if 'rest_framework.permissions.IsAuthenticated' not in settings.REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES']:
        settings.REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'].append('rest_framework.permissions.IsAuthenticated')
    
    settings.JWT_EXPIRATION_DELTA = timedelta(minutes=jwt_expiration_delta_min) # to be changed also in client refresh time
    settings.SIMPLE_JWT = {
        # Lifetime of the access token 
        'ACCESS_TOKEN_LIFETIME': settings.JWT_EXPIRATION_DELTA, 
        'REFRESH_TOKEN_LIFETIME': timedelta(days=36500),  # roughly 100 years
        'ROTATE_REFRESH_TOKENS': False,  # Optional, can rotate tokens on access token refresh
        'BLACKLIST_AFTER_ROTATION': False,  
        # Lifetime of the refresh token 
        # 'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=5), 
        # 'SLIDING_TOKEN_LIFETIME': timedelta(days=5), 

        # 'ALGORITHM': 'HS256',
        # 'SIGNING_KEY': settings.SECRET_KEY,
        # 'VERIFYING_KEY': None,
        # 'AUTH_HEADER_TYPES': ('Bearer',),
        # 'USER_ID_FIELD': 'id',
        # 'USER_ID_CLAIM': 'user_id',
        # 'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
        # 'TOKEN_TYPE_CLAIM': 'token_type',
    }
    
    if use_whitenoise:
        # Configure static files for Whitenoise
        staticFolderName = 'static'
        if not hasattr(settings, 'STATIC_ROOT' ) or not settings.STATIC_ROOT:
            settings.STATIC_ROOT = os.path.join(settings.BASE_DIR.parent, staticFolderName) 
            # check if the static folder exists and create it if not
            if not os.path.exists(settings.STATIC_ROOT):
                os.makedirs(settings.STATIC_ROOT)
        if not hasattr(settings, 'STATIC_URL') or not settings.STATIC_URL:
            settings.STATIC_URL = f'/{staticFolderName}/'

        if not hasattr(settings, 'STORAGES'):
            settings.STORAGES = {
                f"{staticFolderName}": {
                    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
                },
                f"staticfiles": {
                    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
                },
            }

    if not hasattr(settings, 'MEDIA_ROOT'):
        settings.MEDIA_ROOT = os.path.join(settings.BASE_DIR.parent, 'media')
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
    if not hasattr(settings, 'MEDIA_URL'):
        settings.MEDIA_URL = '/media/'

def lastDjangoIndex(settings):
    index = 0
    for i, app in enumerate(settings.INSTALLED_APPS):
        if app.startswith('django'):
            index = i
    return index + 1
