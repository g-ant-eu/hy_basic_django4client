
# A simple JWT and Whitenoise django integration module

## Usage

Inside settings.py add at the end:

```python
import hy_basic_django4client 
import sys
hy_basic_django4client.config.configure_django(sys.modules[__name__])

hy_basic_django4client.config.configure_cors(s,
    allowed_hosts=[".localhost","0.0.0.0","127.0.0.1","[::1]","django"],
    cors_allowed_origins=["http://localhost:6677","http://localhost:8081"],
    csrf_trusted_origins=["http://localhost:6677","http://localhost:8081"]    
    )
```

This enables the project to use JWT and Whitenoise as well as basic cors and csrf.


Inside urls.py add the url configuration to configure JWT login:

```python
from hy_basic_django4client.jwt import JWTAuthHandler
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/static/index.html'), name='index'), # Redirect to the index.html file if you need to
    path('admin/', admin.site.urls),
]

JWTAuthHandler.configure_urls(urlpatterns) # add url configuration for JWT tokens
```

Then protect your views like:

```python
from hy_basic_django4client.jwt import JWTAuthHandler

user = JWTAuthHandler(request)
if not user:
    return JWTAuthHandler.get_error_result()