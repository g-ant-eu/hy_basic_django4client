
# A simple JWT and Whitenoise django integration module

## Usage

Inside settings.py add at the end:

```python
import hy_basic_django4client 
import sys
hy_basic_django4client.config.configure_django(sys.modules[__name__])
```

This enables the project to use JWT and Whitenoise.


Inside urls.py add the url configuration:

```python
from hy_basic_django4client.jwt import JWTAuthHandler
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/static/index.html'), name='index'), # Redirect to the index.html file if you need to
    path('admin/', admin.site.urls),
]

JWTAuthHandler.configure_urls(urlpatterns) # add url configuration for JWT tokens
```